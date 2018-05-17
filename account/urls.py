from django.urls import path

from .views import account_update, account_update_with_login_errors


app_name = 'account'

urlpatterns = [
    # ex: /account/5/
    path(r'update/<int:user_id>/', account_update, name='AccountUpdate'),
    # use this url to pass errors which occurred while creating reports
    # --- some reports require login to social network before
    path(r'update/<int:user_id>/<str:login_to_facebook_error>-<str:login_to_twitter_error>',
         account_update_with_login_errors, name='AccountUpdateWithLoginErrors'),
]
