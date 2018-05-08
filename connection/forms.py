from django import forms
from django.utils.translation import ugettext_lazy as _

from connection.models import Connection


class ConnectionForm(forms.ModelForm):

    class Meta:
        model = Connection
        fields = (
            'user',
            'hash_tag',
            'day_of_report',
            'report_type',
            'twitter_link',
            'number_in_table_twitter',
            'facebook_link',
            'number_in_table_facebook',
        )
        exclude = (
            'user',
        )

    def clean(self):
        data = super(ConnectionForm, self).clean()

        if not any(
            data.get(field, '')
            for field in (
                'facebook_link',
                'twitter_link',
            )
        ):
            self._errors['facebook_link'] = \
                self.error_class([_("You must fill at least one field: Facebook or Twitter.")])
            self._errors['twitter_link'] = \
                self.error_class([_("You must fill at least one field: Facebook or Twitter.")])
        return data

    def clean_hash_tag(self):
        hash_tag = self.cleaned_data['hash_tag']
        qs = Connection.objects.filter(user=self.user).filter(hash_tag=hash_tag)
        if self.instance.pk is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Hash tag('%s') is not unique!" % hash_tag)

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return hash_tag
