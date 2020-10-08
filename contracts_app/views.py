from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .models import Contract, RequestForMaterial, InvoiceForPayment
from .forms import ContractForm, RequestForMaterialForm, InvoiceForPaymentForm
from construction_objects_app.models import ConstructionObject
import telebot

GENERAL_BOT_TOKEN = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'
general_bot = telebot.TeleBot(GENERAL_BOT_TOKEN)
channel_id = '-1001342160485'


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        context['construction_object'] = construction_object
        return context
    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        contract =  self.get_object()
        request_for_materials = RequestForMaterial.objects.filter(contract=contract)
        for request_for_material in request_for_materials:
            if all(invoice.is_done == True for invoice in request_for_material.invoice_for_payment.all()) and list(
                    request_for_material.invoice_for_payment.all()) != []:
                request_for_material.is_done = True
                request_for_material.save()
        if check_user(request.user, ['accountant'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialCreateView(generic.CreateView):
    model = RequestForMaterial
    form_class = RequestForMaterialForm

    def get_success_url(self, **kwargs):
        return reverse('contract_detail', kwargs={'slug': self.kwargs['contract']})

    def send_message(self, contract, doc_file):
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Новая заявка!\n'
        message += 'Объект: ' + contract.construction_object.name + '\n'
        message += 'Работа: ' + contract.name + '\n'
        general_bot.send_message(channel_id, text=message)
        general_bot.send_document(channel_id, doc_file)

    def form_valid(self, form):
        contract = Contract.objects.get(slug=self.kwargs['contract'])
        form.instance.contract = contract
        form.instance.name = 'Заявка ' + str(contract.request_for_material.all().count() + 1)
        self.send_message(contract, form.instance.doc_file)
        return super(RequestForMaterialCreateView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['contract'])
        if check_user(request.user, ['accountant'], construction_object) == 404:
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
        if check_user(request.user, ['accountant'], construction_object) == 404:
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
        if check_user(request.user, ['accountant'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        context['construction_object'] = construction_object
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentCreateView(generic.CreateView):
    model = InvoiceForPayment
    # fields = ['request_for_material', 'bin', 'name_company', 'comment', 'is_cash', 'doc_file']
    form_class = InvoiceForPaymentForm

    def get_success_url(self, **kwargs):
        return reverse('request_for_material_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        request_for_material = RequestForMaterial.objects.get(id=self.kwargs['pk'])
        form.instance.request_for_material = request_for_material
        return super(InvoiceForPaymentCreateView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(contract__request_for_material__id=self.kwargs['pk'])
        request_for_material = RequestForMaterial.objects.get(id=self.kwargs['pk'])
        context['construction_object'] = construction_object
        context['request_for_material'] = request_for_material
        context['invoices'] = InvoiceForPayment.objects.all().values_list('bin', 'name_company').distinct()
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentUpdateView(generic.UpdateView):
    model = InvoiceForPayment
    form_class = InvoiceForPaymentForm

    def get_success_url(self, **kwargs):
        return reverse('request_for_material_detail',
                       kwargs={'pk': RequestForMaterial.objects.get(invoice_for_payment__id=self.kwargs['pk']).id})

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__request_for_material__invoice_for_payment__id=self.kwargs['pk'])
        if check_user(request.user, ['accountant', 'manager'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__id=self.kwargs['pk'])
        request_for_material = RequestForMaterial.objects.get(invoice_for_payment__id=self.kwargs['pk'])
        context['construction_object'] = construction_object
        context['request_for_material'] = request_for_material
        context['invoices'] = InvoiceForPayment.objects.all().values_list('bin', 'name_company').distinct()
        return context


@login_required(login_url='/accounts/login/')
def invoice_delete(request):
    invoice = InvoiceForPayment.objects.get(id=request.POST['id'])
    construction_object = ConstructionObject.objects.get(contract__request_for_material__invoice_for_payment=invoice)
    if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
            request.user.construction_objects.all()):
        return render(request, template_name='404.html')
    red = '/request/' + str(invoice.request_for_material.id) + '/detail/'
    invoice.delete()
    return redirect(red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentDetailView(generic.DetailView):
    model = InvoiceForPayment

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__id=self.kwargs['pk'])
        if check_user(request.user, ['accountant'], construction_object) == 404:
            return render(request, '404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__id=self.kwargs['pk'])
        context['construction_object'] = construction_object
        return context
