from django.db import models
from django.contrib.auth.models import User


class Connection(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Користувач',
    )
    hash_tag = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        verbose_name='Хеш тег',
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
        ("simple", "Звичайний"),
        ("numbered", "Пронумерований"),
        ("full", "Повний"),
    )
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE__CHOICES,
        verbose_name="Тип звіту",
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
        ("mon", "Понеділок"),
        ("tues", "Вівторок"),
        ("wed", "Середа"),
        ("thurs", "Четвер"),
        ("fri", "П'ятниця"),
        ("sat", "Субота"),
        ("sun", "Неділя"),
    )
    day_of_report = models.CharField(
        max_length=30,
        choices=DAY_OF_REPORT__CHOICES,
        verbose_name="День тижня для звіту",
        blank=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Дата створення',
    )

    class Meta:
        ordering = ['hash_tag']
        verbose_name = "Connection"
        verbose_name_plural = "Connections"

    def __str__(self):
        return self.hash_tag
