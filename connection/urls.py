from django.urls import path

from . import views


app_name = 'connection'

urlpatterns = [
    # ex: /connection/
    path('', views.show_connections, name='ShowConnections'),
    path('edit/<int:connection_id>/', views.edit_connection, name='EditConnection'),
    path('delete/<int:connection_id>/', views.delete_connection, name='DeleteConnection'),
]
