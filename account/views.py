from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied

from .models import Account
from .forms import UserForm


@login_required()  # only logged in users should access this
def account_update(request, user_id):
    # if superuser redirect to admin panel
    if request.user.is_superuser:
        return redirect('admin:index')
    # querying the User object with pk from url
    user = User.objects.get(pk=user_id)

    # prepopulate UserForm with retrieved user values from above.
    user_form = UserForm(instance=user)

    # The sorcery begins from here, see explanation below
    AccountInlineFormset = inlineformset_factory(User, Account,
                                                 fields=(
                                                     'facebook_link',
                                                     'twitter_link',
                                                     'facebook_link',
                                                     'twitter_link',
                                                     'eth_wallet',
                                                     'show_eth_wallet_in_report',
                                                     'link_to_bitcointalk_profile',
                                                     'show_link_to_bitcointalk_profile_in_report',
                                                     'nickname_on_bitcointalk',
                                                     'show_nickname_on_bitcointalk_in_report',
                                                     'link_to_telegram_account',
                                                     'show_link_to_telegram_accoun_in_report',
                                                 ),
                                                 can_delete=False,
    )
    formset = AccountInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserForm(request.POST, request.FILES, instance=user)
            formset = AccountInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = AccountInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return redirect('account:AccountUpdate', user_id=user_id)

        return render(request, "account/account_update.html", {
            "user_id": user_id,
            "user_form": user_form,
            "formset": formset,
        })
    else:
        raise PermissionDenied
