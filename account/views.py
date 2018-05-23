from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django import forms

from social_django.models import UserSocialAuth

from .models import Account
from .forms import UserForm


@login_required()  # only logged in users should access this
def account_update(request, user_id):
    # querying the User object with pk from url
    user = User.objects.get(pk=user_id)

    # populate UserForm with retrieved user values from above.
    user_form = UserForm(instance=user)

    # The sorcery begins from here, see explanation below
    account_inline_formset = forms.models.inlineformset_factory(User, Account,
                                                                fields=(
                                                                    'facebook_link',
                                                                    'total_count_of_followers_on_facebook',
                                                                    'eth_wallet',
                                                                    'show_eth_wallet_in_report',
                                                                    'link_to_bitcointalk_profile',
                                                                    'show_link_to_bitcointalk_profile_in_report',
                                                                    'nickname_on_bitcointalk',
                                                                    'show_nickname_on_bitcointalk_in_report',
                                                                    'link_to_telegram_account',
                                                                    'show_link_to_telegram_accoun_in_report',
                                                                ),
                                                                widgets={
                                                                    'facebook_link': forms.TextInput(
                                                                        attrs={
                                                                            'placeholder':
                                                                                "https://www.facebook.com/BillGates/"
                                                                        }),
                                                                },
                                                                can_delete=False,
                                                                )
    formset = account_inline_formset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserForm(request.POST, request.FILES, instance=user)
            formset = account_inline_formset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = account_inline_formset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return redirect('account:AccountUpdate', user_id=user_id)

        try:
            twitter_login = user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        return render(request, "account/account_update.html", {
            "user_id": user_id,
            "user_form": user_form,
            "formset": formset,
            'twitter_login': twitter_login,
            'facebook_login': facebook_login,
        })
    else:
        raise PermissionDenied


@login_required()  # only logged in users should access this
def account_update_with_login_errors(request, user_id, login_to_twitter_error, login_to_facebook_error):
    # querying the User object with pk from url
    user = User.objects.get(pk=user_id)

    # prepopulate UserForm with retrieved user values from above.
    user_form = UserForm(instance=user)

    # The sorcery begins from here, see explanation below
    account_inline_formset = forms.models.inlineformset_factory(User, Account,
                                                                fields=(
                                                                    'facebook_link',
                                                                    'total_count_of_followers_on_facebook',
                                                                    'eth_wallet',
                                                                    'show_eth_wallet_in_report',
                                                                    'link_to_bitcointalk_profile',
                                                                    'show_link_to_bitcointalk_profile_in_report',
                                                                    'nickname_on_bitcointalk',
                                                                    'show_nickname_on_bitcointalk_in_report',
                                                                    'link_to_telegram_account',
                                                                    'show_link_to_telegram_accoun_in_report',
                                                                ),
                                                                widgets={
                                                                    'facebook_link': forms.TextInput(
                                                                        attrs={
                                                                            'placeholder':
                                                                                "https://www.facebook.com/BillGates/"
                                                                        }),
                                                                },
                                                                can_delete=False,
                                                                )
    formset = account_inline_formset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserForm(request.POST, request.FILES, instance=user)
            formset = account_inline_formset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = account_inline_formset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return redirect('account:AccountUpdateWithLoginErrors',
                                    user_id=user_id, login_to_facebook_error=login_to_facebook_error,
                                    login_to_twitter_error=login_to_twitter_error
                                    )

        try:
            twitter_login = user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        return render(request, "account/account_update.html", {
            "user_id": user_id,
            "user_form": user_form,
            "formset": formset,
            'twitter_login': twitter_login,
            'facebook_login': facebook_login,
            'login_to_facebook_error': login_to_facebook_error,
            'login_to_twitter_error': login_to_twitter_error,
        })
    else:
        raise PermissionDenied
