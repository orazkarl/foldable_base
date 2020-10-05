from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .models import Contract, RequestForMaterial
from .forms import ContractForm, RequestForMaterialForm
from construction_objects_app.models import ConstructionObject


def check_user(user, roles, construction_object):
    if construction_object not in list(user.construction_objects.all()):
        return 404
    for role in roles:
        if user.role == role:
            return 404
    return 200


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractCreateView(generic.CreateView):
    model = Contract
    success_url = '/construction_objects/nurly-tau/1'
    form_class = ContractForm

    def form_valid(self, form):
        construction_object = get_object_or_404(ConstructionObject, slug=self.kwargs['construction_object'])
        form.instance.construction_object = construction_object

        return super(ContractCreateView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        construction_object = get_object_or_404(ConstructionObject, slug=self.kwargs['construction_object'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContractCreateView, self).get_context_data(**kwargs)
        construction_object = get_object_or_404(ConstructionObject, slug=self.kwargs['construction_object'])
        context['construction_object'] = construction_object
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractUpdateView(generic.UpdateView):
    model = Contract
    form_class = ContractForm
    success_url = '/construction_objects/nurly-tau/1'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        context['construction_object'] = construction_object
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractDetailView(generic.DetailView):
    model = Contract

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        context['construction_object'] = construction_object
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialCreateView(generic.CreateView):
    model = RequestForMaterial
    form_class = RequestForMaterialForm

    def get_success_url(self, **kwargs):
        return reverse('contract_detail', kwargs={'slug': self.kwargs['contract']})

    def form_valid(self, form):
        contract = Contract.objects.get(slug=self.kwargs['contract'])
        form.instance.contract = contract
        form.instance.name = 'Заявка ' + str(contract.request_for_material.all().count() + 1)
        return super(RequestForMaterialCreateView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['contract'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['contract'])
        contract = Contract.objects.get(slug=self.kwargs['contract'])
        context['construction_object'] = construction_object
        context['contract'] = contract
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialUpdateView(generic.UpdateView):
    model = RequestForMaterial
    form_class = RequestForMaterialForm

    def get_success_url(self, **kwargs):
        return reverse('contract_detail',
                       kwargs={'slug': Contract.objects.get(request_for_material__id=self.kwargs['pk']).slug})

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        contract = Contract.objects.get(request_for_material__id=self.kwargs['pk'])
        context['construction_object'] = construction_object
        context['contract'] = contract
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialDetailView(generic.DetailView):
    model = RequestForMaterial

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        context['construction_object'] = construction_object
        return context
