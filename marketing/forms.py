from django import forms

from marketing.models import NewsletterSubscription
from sales.forms import ReCAPTCHAFormMixin


class NewsletterSubscribeForm(ReCAPTCHAFormMixin, forms.ModelForm):

    class Meta:
        model = NewsletterSubscription
        fields = ('email', 'full_name',)
