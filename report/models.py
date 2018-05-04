from django.contrib.auth.models import User
from django.db import models

from connection.models import Connection


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'reports/user_{0}/{1}'.format(instance.user.id, filename)


class Report(models.Model):
    connection = models.ForeignKey(
        to=Connection,
        on_delete=models.PROTECT,
        verbose_name="Зв'язка",
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Користувач",
    )
    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        verbose_name='Назва звіту',
    )
    file = models.FileField(
        upload_to=user_directory_path,
    )
    created_at = models.DateTimeField(auto_now_add=True)
