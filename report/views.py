import datetime
from io import BytesIO
import os
import re
import time
import zipfile

from dateutil.parser import parse

import requests
import tweepy
import facebook

from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth

from connection.models import Connection
from report.forms import CustomReportForm
from report.models import Report
from report_maker.settings import SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET, MEDIA_ROOT

DAY_OF_REPORT__CHOICES = {
    "mon": "Понеділок",
    "tues": "Вівторок",
    "wed": "Середа",
    "thurs": "Четвер",
    "fri": "П'ятниця",
    "sat": "Субота",
    "sun": "Неділя",
}


@login_required(login_url='/login/')
@csrf_exempt
def show_reports(request):
    all_reports = Report.objects.filter(user=request.user).order_by('-created_at', 'name')

    now = timezone.now()
    paginator = Paginator(all_reports, 5)
    page = request.GET.get('page', 1)

    try:
        all_reports = paginator.page(page)
    except PageNotAnInteger:
        all_reports = paginator.page(1)
    except EmptyPage:
        all_reports = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        custom_report_form = CustomReportForm(request.POST)

        start_date_str = custom_report_form['start_date'].value()
        end_date_str = custom_report_form['end_date'].value()
        day_of_week_key = custom_report_form['day_of_report'].value()
        day_of_week = DAY_OF_REPORT__CHOICES.get(day_of_week_key)

        create_reports(request=request, start_date=start_date_str.replace('/', '.'),
                       end_date=end_date_str.replace('/', '.'), day_of_week=day_of_week)
        return HttpResponseRedirect(reverse('report:ShowReports'))
    else:
        custom_report_form = CustomReportForm()

    return render_to_response(
        'report/report.html',
        {
            'request': request,
            'all_reports': all_reports,
            'page_request_var': paginator,
            'now': now,
            'custom_report_form': custom_report_form,
        },
        RequestContext(request),
    )


@login_required(login_url='/login/')
@csrf_exempt
def create_reports(request, start_date, end_date, day_of_week):
    # convert start_date and end_date from string to datetime.datetime object
    start_date_datetime_object = datetime.datetime.strptime(start_date, '%d.%m.%Y')
    end_date_datetime_object = datetime.datetime.strptime(end_date, '%d.%m.%Y')

    # if date range in custom range form passed wrong - redirect to Show Reports
    # and prevent making reports with wrong args
    if start_date_datetime_object >= end_date_datetime_object:
        return HttpResponseRedirect(reverse('report:ShowReports'), )

    # we receive day_of_week in human readable format and should translate it to machine readable.Example: Понеділок-mon
    for key, value in DAY_OF_REPORT__CHOICES.items():
        if value == day_of_week:
            day_of_week = key

    # get all connections which have day_of_report=day_of_week. Day of week should be in machine readable format
    # 'cause we store day_of_report attribute data of Connection models in maachine readable format
    all_connections = Connection.objects.filter(user=request.user, day_of_report=day_of_week)
    try:
        facebook_login = request.user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    try:
        twitter_login = request.user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    login_to_facebook_error = None
    login_to_twitter_error = None

    # check is any connection from connections with specified day of report(which we mentioned before)
    # have to parse facebook(has facebook link not null) but user is not signed in to facebook account
    if all_connections.filter(facebook_link=None).count() != all_connections.count() and not facebook_login:
        login_to_facebook_error = "Login to Facebook first"

    # check is any connection from connections with specified day of report(which we mentioned before)
    # have to parse twitter(has twitter link not null) but user is not signed in to twitter account
    if all_connections.filter(twitter_link=None).count() != all_connections.count() and not twitter_login:
        login_to_twitter_error = "Login to Twitter first"

    # redirect to Account Settings and pass errors which occurred
    # --- some reports require login to social network before
    if login_to_facebook_error or login_to_twitter_error:
        return HttpResponseRedirect(reverse('account:AccountUpdateWithLoginErrors',
                                            kwargs={
                                                'user_id': request.user.pk,
                                                'login_to_facebook_error': login_to_facebook_error,
                                                'login_to_twitter_error': login_to_twitter_error
                                                }
                                            )
                                    )
    # if user is signed in to all social networks that are required to each report
    # - start to making reports for all connections with mentioned day_of_report
    else:
        user = User.objects.get(pk=request.user.pk)

        for connection in all_connections:
            name_of_file_with_report = connection.hash_tag
            # form filename for report that will be created
            filename = name_of_file_with_report + '__' + start_date + '-' + end_date + '.txt'

            # skip making the report of connection if it's already exists
            #  --- TIP: file name with report is unique
            if Report.objects.filter(name=filename).exists():
                continue

            # create report file with file_name = hash_tag(name of connection) + date range
            # 'cause we create reports for same connections(same hash tags) for different date ranges
            # --- add date ranges to make difference between file names
            f = open(filename, "w+")

            f.write("Period: {} - {}\n\n".format(start_date, end_date))
            if user.account.show_eth_wallet_in_report:
                f.write("Ether: {}".format(user.account.eth_wallet))
            if user.account.show_link_to_bitcointalk_profile_in_report:
                f.write("BitcoinTalk Profile Link: {}".format(user.account.link_to_bitcointalk_profile))
            if user.account.show_nickname_on_bitcointalk_in_report:
                f.write("BitcoinTalk Username: {}".format(user.account.nickname_on_bitcointalk))
            if user.account.show_link_to_telegram_accoun_in_report:
                f.write("Telegram Profile Link: {}\n".format(user.account.link_to_telegram_account))

            # making report Twitter(parsing user twitter page)
            if connection.twitter_link:
                # Connect to Twitter API using access token and secret of our app(registered in Twitter for developers)
                # and access token and secret of signed in User
                twitter_login = user.social_auth.get(provider='twitter')
                access_secret = twitter_login.access_token.get('oauth_token_secret')
                access_token = twitter_login.access_token.get('oauth_token')
                auth = tweepy.OAuthHandler(consumer_key=SOCIAL_AUTH_TWITTER_KEY,
                                           consumer_secret=SOCIAL_AUTH_TWITTER_SECRET)
                auth.set_access_token(access_token, access_secret)
                api = tweepy.API(auth, wait_on_rate_limit=True, )

                link_to_user_twitter_account = "https://twitter.com/" + api.me().screen_name
                full_link_to_tweet = link_to_user_twitter_account + "/status/"

                list_of_tweet_objects = []
                list_of_retweet_objects = []
                number_of_tweets_in_report = 0
                number_of_retweets_and_likes_in_report = 0
                full_link_to_source_page_of_retweet = connection.twitter_link

                f.write("Twitter Campaign\n")
                f.write("Twitter: {}\n".format(link_to_user_twitter_account))
                f.write("Followers: {}\n".format(api.me().followers_count))

                if connection.number_in_table_twitter:
                    f.write("Number on the spreadsheet: {}\n".format(connection.number_in_table_twitter))

                f.write("\nTweets\n")

                for tweet in tweepy.Cursor(api.user_timeline, user=api.me().screen_name, tweet_mode="extended").items():
                    created_at = datetime.datetime(tweet.created_at.year, tweet.created_at.month, tweet.created_at.day,)
                    if (created_at > start_date_datetime_object) \
                            and (created_at <= end_date_datetime_object):
                        is_retweet = False

                        if hasattr(tweet, 'quoted_status'):  # if message added by user to retweet
                            full_link_to_source_of_retweet = "https://twitter.com/" + \
                                                             tweet.quoted_status.user.screen_name
                            is_retweet = True
                        elif hasattr(tweet, 'retweeted_status'):  # if retweet WITHOUT message added by user
                            full_link_to_source_of_retweet = "https://twitter.com/" + \
                                                             tweet.retweeted_status.user.screen_name
                            is_retweet = True
                        else:
                            full_link_to_source_of_retweet = ""

                        for hashtag in tweet.entities['hashtags']:
                            # use casefold() to do case insensitive matching
                            # casefold better than lower() `cause work fine with characters like this: "Maße"
                            if not is_retweet and hashtag['text'].casefold() == connection.hash_tag.casefold():
                                list_of_tweet_objects.append(tweet)
                                break

                        # connection.twitter_link --- not None
                        if connection.twitter_link.casefold() == full_link_to_source_of_retweet.casefold():
                            list_of_retweet_objects.append(tweet)

                # check connection.report_type
                # and according to it choose which format of str_line to use and what to write
                # write all tweets to 'Tweets' section of report &
                # write all Retweets(We need only retweets!)
                # to 'Retweets and Likes'(Yes! Name of section is another:) section of report
                if connection.report_type == "simple":
                    str_line_to_write = "{}\n"

                    for tweet in list_of_tweet_objects:
                        f.write(str_line_to_write.format(full_link_to_tweet + str(tweet.id)))

                    f.write("\n\nRetweets and Likes\n")

                    for retweet in list_of_retweet_objects:
                        number_of_retweets_and_likes_in_report += 1
                        full_link_to_retweet = \
                            get_full_link_of_retweet_in_source_page(
                                retweet=retweet, full_link_to_source_page_of_retweet=full_link_to_source_page_of_retweet
                            )  # use this function to get link
                        f.write(str_line_to_write.format(full_link_to_retweet))

                elif connection.report_type == "numbered":
                    str_line_to_write = "{}. {}\n"

                    for tweet in list_of_tweet_objects:
                        number_of_tweets_in_report += 1
                        f.write(str_line_to_write.format(number_of_tweets_in_report,
                                                         full_link_to_tweet + str(tweet.id)))

                    f.write("\n\nRetweets and Likes\n")

                    for retweet in list_of_retweet_objects:
                        number_of_retweets_and_likes_in_report += 1
                        full_link_to_retweet = \
                            get_full_link_of_retweet_in_source_page(
                                retweet=retweet, full_link_to_source_page_of_retweet=full_link_to_source_page_of_retweet
                            )  # use this function to get link
                        f.write(str_line_to_write.format(number_of_retweets_and_likes_in_report, full_link_to_retweet))

                else:  # connection.report_type == "full"
                    str_line_to_write = "{} - {:%d.%m}: {}\n"

                    for tweet in list_of_tweet_objects:
                        number_of_tweets_in_report += 1
                        f.write(str_line_to_write.format(number_of_tweets_in_report,
                                                         tweet.created_at, full_link_to_tweet + str(tweet.id)))

                    f.write("\n\nRetweets and Likes\n")

                    for retweet in list_of_retweet_objects:
                        number_of_retweets_and_likes_in_report += 1
                        full_link_to_retweet = \
                            get_full_link_of_retweet_in_source_page(
                                retweet=retweet, full_link_to_source_page_of_retweet=full_link_to_source_page_of_retweet
                            )  # use this function to get link
                        f.write(str_line_to_write.format(number_of_retweets_and_likes_in_report, retweet.created_at,
                                                         full_link_to_retweet))

            # making report Facebook(parsing user Facebook page)
            if connection.facebook_link:
                # Connect to Facebook API using signed in User access token
                facebook_login = user.social_auth.get(provider='facebook')
                access_token = facebook_login.extra_data['access_token']

                graph = facebook.GraphAPI(access_token=access_token, version="2.7")

                # convert start and end dates to Unix time format
                # to use it for parsing Facebook(to use since&until fields calling API)
                fields = "message,parent_id,created_time"
                end_date_datetime_object += datetime.timedelta(days=1)  # add 1 day to include all posts during end_date
                since_unixtime = time.mktime(start_date_datetime_object.timetuple())
                until_unixtime = time.mktime(end_date_datetime_object.timetuple())

                # specify all arguments(in our case only fields which we require)
                # which API object should use for connection to Facebook API
                args = {'fields': fields, 'since': since_unixtime, "until": until_unixtime}
                posts = graph.get_connections(id='me', connection_name='posts', **args)

                profile_permissions = graph.get_connections(id='me', connection_name='permissions', )['data']

                for permission in profile_permissions:
                    if permission['permission'] == 'user_posts' and permission['status'] == 'granted':
                        break
                    else:
                        return HttpResponseRedirect(reverse('account:AccountUpdateWithLoginErrors',
                                                            kwargs={
                                                                'user_id': request.user.pk,
                                                                'login_to_facebook_error':
                                                                    'Grand permission to view user posts!',
                                                                'login_to_twitter_error': login_to_twitter_error
                                                            }
                                                            )
                                                    )

                if connection.twitter_link:
                    f.write("\n\n-----------------\n\n")
                f.write("Facebook Campaign\n")
                f.write("Facebook: {}\n".format(user.account.facebook_link))
                f.write("Followers: {}\n".format(user.account.total_count_of_followers_on_facebook))
                if connection.number_in_table_facebook:
                    f.write("Number on the spreadsheet: {}\n".format(connection.number_in_table_facebook))
                f.write("\nPosts\n")

                list_of_post_objects = []
                list_of_repost_and_shares_objects = []
                number_of_posts_in_report = 0
                number_of_reposts_and_shares_in_report = 0

                while True:
                    try:
                        # Perform some action on each post in the collection we receive from
                        # Facebook.
                        for post in posts['data']:
                            is_share = False
                            try:
                                # parent_id looks like - 11111111_99999999
                                # first part - id of user(owner of reposted status), second - post_id
                                if post['parent_id'].split('_')[0] == connection.facebook_link:
                                    list_of_repost_and_shares_objects.append(post)
                                    is_share = True
                            except KeyError:
                                pass

                            try:
                                if post['message']:  # get full message and search where for hashtag
                                    container_of_found_hash_tag = re.findall(r"#" + connection.hash_tag.casefold(),
                                                                             post['message'].casefold())
                                    # if current post is not share or re-post add it ti list of posts with hash tag
                                    if container_of_found_hash_tag and not is_share:
                                        list_of_post_objects.append(post)
                            except KeyError:
                                pass

                        # Attempt to make a request to the next page of data, if it exists.
                        posts = requests.get(posts['paging']['next']).json()
                    except KeyError:
                        # When there are no more pages (['paging']['next']), break from the
                        # loop and end the script.
                        break

                # check connection.report_type
                # and according to it choose which format of str_line to use and what to write
                # write all posts to 'Posts' section of report &
                # write all Reposts and Shares
                # to 'Reposts and Shares' section of report
                if connection.report_type == "simple":
                    str_line_to_write = "{}\n"
                    for post in list_of_post_objects:
                        f.write(str_line_to_write.format("https://www.facebook.com/" + post['id']))
                    f.write("\n\nReposts and Shares\n")

                    for repost in list_of_repost_and_shares_objects:
                        f.write(str_line_to_write.format(
                            "https://www.facebook.com/" + repost['id']))
                elif connection.report_type == "numbered":
                    str_line_to_write = "{}. {}\n"
                    for post in list_of_post_objects:
                        number_of_posts_in_report += 1
                        f.write(str_line_to_write.format(number_of_posts_in_report,
                                                         "https://www.facebook.com/" + post['id']))
                    f.write("\n\nReposts and Shares\n")

                    for repost in list_of_repost_and_shares_objects:
                        number_of_reposts_and_shares_in_report += 1
                        f.write(str_line_to_write.format(number_of_reposts_and_shares_in_report,
                                                         "https://www.facebook.com/" + repost['id']))
                else:  # connection.report_type == "full"
                    str_line_to_write = "{} - {:%d.%m}: {}\n"
                    for post in list_of_post_objects:
                        number_of_posts_in_report += 1
                        # convert 'created_time' to datetime object and
                        # skip part with timezones in datetime object to compare with datetime objects without tz
                        creation_time_datetime_object_with_tz = parse(post['created_time'])
                        creation_time_datetime_str = \
                            creation_time_datetime_object_with_tz.strftime("%d.%m.%Y")
                        creation_time_datetime_object = \
                            datetime.datetime.strptime(creation_time_datetime_str, '%d.%m.%Y')

                        f.write(str_line_to_write.format(number_of_posts_in_report, creation_time_datetime_object,
                                                         "https://www.facebook.com/" + post['id']))
                    f.write("\n\nReposts and Shares\n")

                    for repost in list_of_repost_and_shares_objects:
                        number_of_reposts_and_shares_in_report += 1
                        # convert 'created_time' to datetime object and
                        # skip part with timezones in datetime object to compare with datetime objects without tz
                        creation_time_datetime_object_with_tz = parse(repost['created_time'])
                        creation_time_datetime_str = \
                            creation_time_datetime_object_with_tz.strftime("%d.%m.%Y")
                        creation_time_datetime_object = \
                            datetime.datetime.strptime(creation_time_datetime_str, '%d.%m.%Y')

                        f.write(str_line_to_write.format(number_of_reposts_and_shares_in_report,
                                                         creation_time_datetime_object,
                                                         "https://www.facebook.com/" + repost['id']))
            f.close()

            report = Report(
                user=user,
                connection=connection,
                name=f.name,  # name reports as file with reports in zip archive (name: reports_<date range>.zip)
                file=f,
            )
            report.save()

            # if temporary file exists, delete it
            # file with report is uploaded to db of reports
            if os.path.isfile(f.name):
                os.remove(f.name)

        return HttpResponseRedirect(reverse('report:ShowReports'), )


@login_required(login_url='/login/')
def download_file(request, filename):
    path = MEDIA_ROOT + "/reports/user_" + str(request.user.pk) + "/"
    data = open(path + filename, "rb").read()
    response = HttpResponse(data, content_type='application/vnd')
    response['Content-Length'] = os.path.getsize(path + filename)
    return response


@login_required(login_url='/login/')
def download_all_reports(request):
    reports = Report.objects.filter(user=request.user)
    filenames = []
    path = MEDIA_ROOT + "/reports/user_" + str(request.user.pk) + "/"
    # Files (local path) to put in the .zip
    for report in reports:
        filenames.append(path + report.name)

    if not filenames:
        return HttpResponseRedirect(reverse('report:ShowReports'), )

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    zip_subdir = "reports"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


@login_required(login_url='/login/')
def delete_report(request, report_id=None):
    instance = Report.objects.filter(id=report_id)
    instance.delete()
    return HttpResponseRedirect(reverse('report:ShowReports'))


@login_required(login_url='/login/')
def delete_all_reports(request):
    reports = Report.objects.filter(user=request.user)
    for report in reports:
        report.delete()
    return HttpResponseRedirect(reverse('report:ShowReports'))


def privacy_policy(request):
    return render_to_response(template_name='report_maker/privacypolicy.htm')


# Use this function to get full link of retweet in page from which user retweeted status in Twitter & minimize code
def get_full_link_of_retweet_in_source_page(retweet, full_link_to_source_page_of_retweet):
    if hasattr(retweet, 'retweeted_status'):
        full_link_to_retweet = full_link_to_source_page_of_retweet + \
                               "/status/" + retweet.retweeted_status.id_str
    else:  # if tweet quoted_status is True
        full_link_to_retweet = full_link_to_source_page_of_retweet + \
                               "/status/" + retweet.quoted_status.id_str
    return full_link_to_retweet
