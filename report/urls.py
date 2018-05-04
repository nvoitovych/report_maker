from django.urls import path

from . import views


app_name = 'report'

urlpatterns = [
    # ex: /reports/
    path('', views.show_reports, name='ShowReports'),
    path('delete/<int:report_id>/', views.delete_report, name='DeleteReport'),
    path('delete/<str:day_of_report>/', views.create_reports, name='CreateReport'),
]