from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from appbase.models import Object, Contract
from material_app.models import Material
from .filters import MaterialFilter


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AnalyticsView(generic.ListView):
    template_name = 'analytics/analytics.html'
    # queryset = Material.objects.filter(is_delivery=True, invoice__is_done=True)
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contracts = Contract.objects.filter(contstruct_object__slug=self.kwargs['slug'])
        queryset = self.get_queryset().filter(is_delivery=True, invoice__is_done=True, invoice__request_mat__contract__contstruct_object__slug=self.kwargs['slug'])
        material_filter = MaterialFilter(self.request.GET, queryset=queryset)

        context['filter'] = material_filter
        return context



    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs['slug']
        self.extra_context = {
            'object': Object.objects.get(slug=object_slug),

            # 'materialFilter': materialFilter,
        }
        return super().get(request, *args, **kwargs)
