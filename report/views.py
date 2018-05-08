import datetime
from time import timezone

from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from connection.models import Connection
from report.forms import DateRangeForm
from report.models import Report


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
        daterange_form = DateRangeForm(request.POST)
        start_date_str = daterange_form['start_date'].value()
        end_date_str = daterange_form['end_date'].value()

        # parse our date in str format('dd/mm/yyyy') and extract day, month, year
        start_date_arr = start_date_str.split("/")
        start_date_year_str = start_date_arr[2]
        start_date_month_str = start_date_arr[1]
        start_date_day_str = start_date_arr[0]
        start_date = datetime.date(day=int(start_date_day_str), month=int(start_date_month_str), year=int(start_date_year_str))
        print(start_date_day_str)
        print(start_date_month_str)
        print(start_date_year_str)
        print(start_date)

        end_date_arr = end_date_str.split("/")
        end_date_year_str = start_date_arr[2]
        end_date_month_str = start_date_arr[1]
        end_date_day_str = start_date_arr[0]

        start_date = datetime.date(day=int(end_date_day_str), month=int(end_date_month_str),
                                   year=int(end_date_year_str))

        #print(end_date)
        return HttpResponseRedirect(reverse('report:ShowReports'))
    else:
        daterange_form = DateRangeForm()

    return render_to_response(
        'report/report.html',
        {
            'request': request,
            'all_reports': all_reports,
            'page_request_var': paginator,
            'now': now,
            'daterange_form': daterange_form,
            # 'connections_on_page': connections_on_page,
        },
        RequestContext(request),
    )


@login_required(login_url='/login/')
@csrf_exempt
def create_reports(request):
    daterange_form = DateRangeForm(request.POST)
    all_connections = Report.objects.filter(user=request.user)
    if daterange_form.is_valid():
        pass

    return HttpResponseRedirect(reverse('report:ShowReports'))


@login_required(login_url='/login/')
@csrf_exempt
def delete_report(request, report_id=None):
    instance = Report.objects.filter(id=report_id)
    instance.delete()
    return HttpResponseRedirect(reverse('report:ShowReports'))
