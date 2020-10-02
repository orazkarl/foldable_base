from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .models import Contract
from .forms import ContractForm
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
