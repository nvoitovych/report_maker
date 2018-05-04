from django.urls import path

from .views import account_update


app_name = 'account'

urlpatterns = [
    # ex: /account/5/
    path(r'update/<int:user_id>/', account_update, name='AccountUpdate'),
]
