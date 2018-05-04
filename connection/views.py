from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from connection.forms import ConnectionForm
from connection.models import Connection


@login_required(login_url='/login/')
@csrf_exempt
def show_connections(request):
    all_connections = Connection.objects.filter(user=request.user).order_by('-created_at', 'hash_tag')

    paginator = Paginator(all_connections, 5)
    page = request.GET.get('page', 1)

    try:
        all_connections = paginator.page(page)
    except PageNotAnInteger:
        all_connections = paginator.page(1)
    except EmptyPage:
        all_connections = paginator.page(paginator.num_pages)
    # connections_on_page = all_connections.end_index() - all_connections.start_index() + 1

    if request.method == 'POST':
        form = ConnectionForm(request.POST)
        form.user = request.user
        if form.is_valid():
            connection = form.save(commit=False)
            connection.user = request.user
            connection.save()
            return HttpResponseRedirect(reverse('connection:ShowConnections'))
    else:
        form = ConnectionForm()

    return render_to_response(
        'connection/connection.html',
        {
            'request': request,
            'add_form': form,
            'all_connections': all_connections,
            'page_request_var': paginator,
            # 'connections_on_page': connections_on_page,
        },
        RequestContext(request),
    )


@login_required(login_url='/login/')
@csrf_exempt
def main_page(request):
    return render(request, "report_maker/main_page.html", {
            'request': request,
        })


@login_required(login_url='/login/')
@csrf_exempt
def edit_connection(request, connection_id=None):
    connection_object = get_object_or_404(Connection, pk=connection_id) if connection_id else None
    if request.method == 'POST':
        form = ConnectionForm(request.POST, instance=connection_object)
        form.user = request.user
        if form.is_valid():
            connection = form.save(commit=False)
            connection.user = request.user
            connection.save()
            return HttpResponseRedirect(reverse('connection:ShowConnections'))
    else:
        data = {
            'user': connection_object.user,
            'hash_tag': connection_object.hash_tag,
            'day_of_report': connection_object.day_of_report,
            'report_type': connection_object.report_type,
            'twitter_link': connection_object.twitter_link,
            'number_in_table_twitter': connection_object.number_in_table_twitter,
            'facebook_link': connection_object.facebook_link,
            'number_in_table_facebook': connection_object.number_in_table_facebook,
        }
        form = ConnectionForm(initial=data)

    return render_to_response(
        'connection/edit_connection.html',
        {
            'request': request,
            'edit_form': form,
            'connection_object': connection_object,
            'connection_id': connection_id,
        },
        RequestContext(request),
    )


@login_required(login_url='/login/')
@csrf_exempt
def delete_connection(request, connection_id=None):
    instance = Connection.objects.filter(id=connection_id)
    instance.delete()
    return HttpResponseRedirect(reverse('connection:ShowConnections'))
