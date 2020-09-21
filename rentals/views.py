from django.shortcuts import render
from django.views.generic import TemplateView


# Function-based view
def home(request):
    context = {'foo': 'bar'}
    return render(request, 'home.html', context=context)


# Class-based view (equivalent to above)
class HomeView(TemplateView):
    template_name = 'home.html'

    # Example of passing context to the template in a class-based view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['foo'] = 'bar'
        return context
