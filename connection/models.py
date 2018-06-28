from django.db import models
from django.contrib.auth.models import User


class Connection(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='User',
    )
    hash_tag = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        verbose_name='Hash tag',
    )
    facebook_link = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Facebook',
    )
    twitter_link = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Twitter',
    )
    REPORT_TYPE__CHOICES = (
        ("simple", "Simple"),
        ("numbered", "Numbered"),
        ("full", "Full"),
    )
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE__CHOICES,
        verbose_name="Type of report",
        blank=False,
    )
    number_in_table_facebook = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    number_in_table_twitter = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    DAY_OF_REPORT__CHOICES = (
        ("mon", "Monday"),
        ("tues", "Tuesday"),
        ("wed", "Wednesday"),
        ("thurs", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    )
    day_of_report = models.CharField(
        max_length=30,
        choices=DAY_OF_REPORT__CHOICES,
        verbose_name="Day of week for report",
        blank=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Date of creation',
    )

    class Meta:
        ordering = ['hash_tag']
        verbose_name = "Connection"
        verbose_name_plural = "Connections"

    def __str__(self):
        return self.hash_tag
