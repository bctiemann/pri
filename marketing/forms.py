from django import forms

from marketing.models import NewsletterSubscription, SurveyResponse
from sales.forms import ReCAPTCHAFormMixin


class NewsletterSubscribeForm(ReCAPTCHAFormMixin, forms.ModelForm):

    class Meta:
        model = NewsletterSubscription
        fields = ('email', 'full_name',)


class NewsletterUnsubscribeForm(forms.Form):
    email = forms.EmailField()


class SurveyResponseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['general_rating'].empty_label = None

    class Meta:
        model = SurveyResponse
        fields = '__all__'
