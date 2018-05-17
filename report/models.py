import os

from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.dispatch import receiver

from connection.models import Connection


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'reports/user_{0}/{1}'.format(instance.user.id, filename)


class Report(models.Model):
    connection = models.ForeignKey(
        to=Connection,
        on_delete=models.CASCADE,
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

    def save(self, *args, **kwargs):
        f = open(self.name, 'r')
        self.file = File(name=self.name, file=File(f))
        super(Report, self).save(*args, **kwargs)


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=Report)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Report` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
