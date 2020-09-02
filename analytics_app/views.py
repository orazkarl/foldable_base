from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from appbase.models import Object, Contract
from material_app.models import Material, ReleaseMaterial, ReleaseMaterialItem
from .filters import MaterialFilter
from django.db.models import Count, Sum


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
        context['total_sum_price'] = material_filter.qs.aggregate(Sum('sum_price'))['sum_price__sum']
        context['filter'] = material_filter


        return context



    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs['slug']
        self.extra_context = {
            'object': Object.objects.get(slug=object_slug),

            # 'materialFilter': materialFilter,
        }
        return super().get(request, *args, **kwargs)

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TotalStats(generic.TemplateView):
    template_name = 'analytics/total_stats.html'

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs['slug']
        self.extra_context = {
            'object': Object.objects.get(slug=object_slug),
        }
        return super().get(request, *args, **kwargs)