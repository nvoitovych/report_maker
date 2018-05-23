from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Account(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Користувач',
    )
    is_online = models.BooleanField(
        default=False,
        verbose_name='Онлайн',
    )
    mobile_phone_number = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Мобільний номер',
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
    total_count_of_followers_on_facebook = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name='К-сть підписників на Facebook',
    )
    eth_wallet = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Ethereum гаманець',
    )
    show_eth_wallet_in_report = models.BooleanField(
        default=False,
        verbose_name="Відображати Ethereum гаманець у звіті?",
    )
    link_to_bitcointalk_profile = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='BitcoinTalk Профіль',
    )
    show_link_to_bitcointalk_profile_in_report = models.BooleanField(
        default=False,
        verbose_name="Відображати посилання на BitcoinTalk аккаунт у звіті?",
    )
    nickname_on_bitcointalk = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Nickname на BitcoinTalk',
    )
    show_nickname_on_bitcointalk_in_report = models.BooleanField(
        default=False,
        verbose_name="Відображати Nickname на BitcoinTalk у звіті?",
    )
    link_to_telegram_account = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Telegram Account',
    )
    show_link_to_telegram_accoun_in_report = models.BooleanField(
        default=False,
        verbose_name="Відображати Telegram Account у звіті?",
    )
    start_date_of_license = models.DateField(
        blank=True,
        null=True,
    )
    end_date_of_license = models.DateField(
        blank=True,
        null=True,
    )
    # contacts_info for ADMIN

    class Meta:
        ordering = ['user']
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
    instance.account.save()
