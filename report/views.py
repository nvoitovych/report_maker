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
def create_reports(request, day_of_report=None):
    all_reports = Report.objects.filter(user=request.user).order_by('-created_at', 'name')

    return HttpResponseRedirect(reverse('report:ShowReports'))


@login_required(login_url='/login/')
@csrf_exempt
def delete_report(request, report_id=None):
    instance = Report.objects.filter(id=report_id)
    instance.delete()
    return HttpResponseRedirect(reverse('report:ShowReports'))
