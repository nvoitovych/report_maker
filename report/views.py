import datetime
import os

import tweepy

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
from report_maker.settings import SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET


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
    # connections_on_page = all_connections.end_index() - all_connections.start_index() + 1

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
            # 'connections_on_page': connections_on_page,
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

            if connection.twitter_link:
                # Connect to Twitter API using access token and secret of our app(registered in Twitter for developers)
                # and access token and secret of signed in User
                twitter_login = user.social_auth.get(provider='twitter')
                access_secret = twitter_login.access_token.get('oauth_token_secret')
                access_token = twitter_login.access_token.get('oauth_token')
                consumer_key = SOCIAL_AUTH_TWITTER_KEY
                consumer_secret = SOCIAL_AUTH_TWITTER_SECRET
                auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_secret)
                api = tweepy.API(auth, wait_on_rate_limit=True, )

                screen_name = api.me().screen_name
                link_to_user_twitter_account = "https://twitter.com/" + screen_name
                full_link_to_tweet = link_to_user_twitter_account + "/status/"

                f.write("Twitter Campaign\n")
                f.write("Twitter: {}\n".format(link_to_user_twitter_account))
                f.write("Followers: {}\n".format(api.me().followers_count))

                if connection.number_in_table_twitter:
                    f.write("Number on the spreadsheet: {}\n".format(connection.number_in_table_twitter))

                f.write("\nTweets\n")

                tweets_list = []
                retweets_and_likes_list = []

                if connection.report_type == "simple":
                    str_line_to_write = "{}\n"
                elif connection.report_type == "numbered":
                    str_line_to_write = "{}. {}\n"
                else:
                    str_line_to_write = "{} - {:%d.%m}: {}\n"

                if connection.report_type == "simple":
                    for tweet in tweepy.Cursor(api.user_timeline, user=screen_name).items():
                        if (tweet.created_at >= start_date_datetime_object) \
                                and (tweet.created_at < end_date_datetime_object):
                            if hasattr(tweet, 'quoted_status'):
                                full_link_to_source_of_retweet = tweet.quoted_status.user.screen_name
                            elif hasattr(tweet, 'retweeted_status'):
                                full_link_to_source_of_retweet = tweet.retweeted_status.user.screen_name
                            else:
                                full_link_to_source_of_retweet = None

                            if full_link_to_source_of_retweet:
                                full_link_to_source_of_retweet = "https://twitter.com/" + full_link_to_source_of_retweet

                            has_this_tweet_hashtag_from_connection = False
                            for hashtag in tweet.entities['hashtags']:
                                if hashtag['text'] == connection.hash_tag:
                                    has_this_tweet_hashtag_from_connection = True

                            if has_this_tweet_hashtag_from_connection:
                                tweets_list.append(full_link_to_tweet + str(tweet.id))

                            # connection.twitter_link --- not None
                            if connection.twitter_link == full_link_to_source_of_retweet:
                                if hasattr(tweet, 'retweeted_status'):
                                    full_link_to_source_of_retweet += "/status/" + tweet.retweeted_status.id_str
                                else:
                                    full_link_to_source_of_retweet += "/status/" + tweet.quoted_status.id_str

                                retweets_and_likes_list.append(full_link_to_source_of_retweet)

                elif connection.report_type == "numbered":
                    number_of_tweets_in_report = 0
                    number_of_retweets_and_likes_in_report = 0
                    for tweet in tweepy.Cursor(api.user_timeline, user=screen_name).items():
                        if (tweet.created_at >= start_date_datetime_object) \
                                and (tweet.created_at < end_date_datetime_object):
                            if hasattr(tweet, 'quoted_status'):
                                full_link_to_source_of_retweet = tweet.quoted_status.user.screen_name
                            elif hasattr(tweet, 'retweeted_status'):
                                full_link_to_source_of_retweet = tweet.retweeted_status.user.screen_name
                            else:
                                full_link_to_source_of_retweet = None

                            if full_link_to_source_of_retweet:
                                full_link_to_source_of_retweet = "https://twitter.com/" + full_link_to_source_of_retweet

                            has_this_tweet_hashtag_from_connection = False
                            for hashtag in tweet.entities['hashtags']:
                                if hashtag['text'] == connection.hash_tag:
                                    has_this_tweet_hashtag_from_connection = True

                            if has_this_tweet_hashtag_from_connection:
                                number_of_tweets_in_report += 1
                                tweets_list.append(str_line_to_write.format(number_of_tweets_in_report,
                                                                            full_link_to_tweet + str(tweet.id)))

                            # add all Retweets
                            # connection.twitter_link --- not None
                            if connection.twitter_link == full_link_to_source_of_retweet:
                                number_of_retweets_and_likes_in_report += 1
                                if hasattr(tweet, 'retweeted_status'):
                                    full_link_to_source_of_retweet += "/status/" + tweet.retweeted_status.id_str
                                else:
                                    full_link_to_source_of_retweet += "/status/" + tweet.quoted_status.id_str

                                retweets_and_likes_list.append(str_line_to_write.format(
                                    number_of_retweets_and_likes_in_report, full_link_to_source_of_retweet))
                else:
                    number_of_tweets_in_report = 0
                    number_of_retweets_and_likes_in_report = 0
                    for tweet in tweepy.Cursor(api.user_timeline, user=screen_name, ).items():

                        if (tweet.created_at >= start_date_datetime_object) \
                                and (tweet.created_at < end_date_datetime_object):
                            if hasattr(tweet, 'quoted_status'):
                                full_link_to_source_of_retweet = tweet.quoted_status.user.screen_name
                            elif hasattr(tweet, 'retweeted_status'):
                                full_link_to_source_of_retweet = tweet.retweeted_status.user.screen_name
                            else:
                                full_link_to_source_of_retweet = None

                            if full_link_to_source_of_retweet:
                                full_link_to_source_of_retweet = "https://twitter.com/" + full_link_to_source_of_retweet
                            has_this_tweet_hashtag_from_connection = False
                            for hashtag in tweet.entities['hashtags']:
                                if hashtag['text'] == connection.hash_tag:
                                    has_this_tweet_hashtag_from_connection = True

                            if has_this_tweet_hashtag_from_connection:
                                number_of_tweets_in_report += 1

                                tweets_list.append(str_line_to_write.format(
                                    number_of_tweets_in_report, tweet.created_at, full_link_to_tweet + str(tweet.id)))

                            # add all Retweets
                            # connection.twitter_link --- not None
                            if connection.twitter_link == full_link_to_source_of_retweet:
                                number_of_retweets_and_likes_in_report += 1
                                if hasattr(tweet, 'retweeted_status'):
                                    full_link_to_source_of_retweet += "/status/" + tweet.retweeted_status.id_str
                                else:
                                    # if tweet quoted_status is True
                                    full_link_to_source_of_retweet += "/status/" + tweet.quoted_status.id_str
                                retweets_and_likes_list.append(str_line_to_write.format(
                                    number_of_retweets_and_likes_in_report, tweet.created_at,
                                    full_link_to_source_of_retweet))

                # write all tweets to 'Tweets' section of report
                for line in tweets_list:
                    f.write(line)
                f.write("\n\nRetweets and Likes\n")
                # write all Retweets(We need only retweets!)
                # to 'Retweets and Likes'(Yes! Name of section is another:) section of report
                for line in retweets_and_likes_list:
                    f.write(line)
            f.close()

            report = Report(
                connection=connection,
                user=user,
                name=f.name,  # name report as file with report(hash_tag + date range)
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
    path = "media/reports/" + request.user.username + '_' + str(request.user.pk) + "/"
    data = open(path + filename, "rb").read()
    response = HttpResponse(data, content_type='application/vnd')
    response['Content-Length'] = os.path.getsize(path + filename)
    return response


@login_required(login_url='/login/')
@csrf_exempt
def delete_report(request, report_id=None):
    instance = Report.objects.filter(id=report_id)
    instance.delete()
    return HttpResponseRedirect(reverse('report:ShowReports'))
