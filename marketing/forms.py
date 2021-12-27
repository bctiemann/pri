from django import forms

from marketing.models import NewsletterSubscription


class NewsletterSubscribeForm(forms.ModelForm):

    class Meta:
        model = NewsletterSubscription
        fields = ('email', 'full_name',)
