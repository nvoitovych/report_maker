from django.contrib.auth.models import User
from django.utils.timezone import now


class UserAuth(object):
    def authenticate(self, request=None, username=None, password=None):
        if request is not None:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and user.is_active:
                    if user.is_superuser == True:
                        return user
                    if user.account.start_date_of_license is not None and user.account.start_date_of_license is not None:
                        if now().date() >= user.account.start_date_of_license and now().date() <= user.account.end_date_of_license:
                            return user
            except User.DoesNotExist:
                return None

    def get_user(self, request):
        try:
            user = User.objects.get(pk=request)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
