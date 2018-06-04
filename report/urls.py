from django.urls import path

from . import views


app_name = 'report'

urlpatterns = [
    # ex: /reports/
    path('', views.show_reports, name='ShowReports'),
    path('delete/<int:report_id>/', views.delete_report, name='DeleteReport'),
    path('delete/', views.delete_all_reports, name='DeleteAllReports'),
    path('download/<str:filename>/', views.download_file, name='DownloadReport'),
    path('download/', views.download_all_reports, name='DownloadAllReports'),
    path('privacy_policy/', views.privacy_policy, name='PrivacyPolicy'),
    path('create/(<start_date>\d{2}-\d{2}-\d{4})_(<end_date>\d{2}-\d{2}-\d{4})_<str:day_of_week>/',
         views.create_reports, name='CreateReports'),
]
