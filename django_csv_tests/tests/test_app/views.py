from django.views.generic import TemplateView
from django_client_data import set_client_data


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        set_client_data(request, **{'foo': 'bar'})
        return super(IndexView, self).get(request, *args, **kwargs)
