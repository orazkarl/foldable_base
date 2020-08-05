from django.shortcuts import render
from django.views import generic
from .models import Object, Contract, Material


class HomeView(generic.ListView):
    template_name = 'index.html'
    queryset = Object.objects.all()


class ObjectDetailView(generic.DetailView):
    template_name = 'object_detail.html'
    model = Object

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs.get(self.slug_url_kwarg, None)

        contracts = Contract.objects.filter(contstruct_object__slug=object_slug)

        self.extra_context = {
            'contracts': contracts,
        }
        return super().get(request, *args, **kwargs)


class ContractDetailView(generic.ListView):
    template_name = 'contract_detail.html'
    # model = Material
    queryset = Material.objects.all()

    def get(self, request, *args, **kwargs):
        contract_slug = self.kwargs['contract_slug']
        object_slug = self.kwargs['slug']
        contract = Contract.objects.get()
        materials = Material.objects.filter(contract=contract)
        self.extra_context = {
            'materials': materials,
        }
        return super().get(request, *args, **kwargs)
