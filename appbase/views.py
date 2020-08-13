from django.shortcuts import render, redirect, HttpResponse
from django.views import generic
from .models import Object, Contract, Material, RequestForMaterial, InvoiceForPayment
from transliterate import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from openpyxl import load_workbook


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class HomeView(generic.ListView):
    template_name = 'index.html'
    queryset = Object.objects.all()


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ObjectDetailView(generic.DetailView):
    template_name = 'appbase/object_detail.html'
    model = Object

    def get(self, request, *args, **kwargs):
        object_slug = self.kwargs.get(self.slug_url_kwarg, None)

        contracts = Contract.objects.filter(contstruct_object__slug=object_slug)

        self.extra_context = {
            'contracts': contracts,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractDetailView(generic.TemplateView):
    template_name = 'appbase/contract/detail.html'

    # model = Material
    # queryset = Material.objects.all()

    def get(self, request, *args, **kwargs):
        contract_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)
        materials = Material.objects.filter(contract=contract)
        self.extra_context = {
            'materials': materials,
            'contract': contract,
            'requests': RequestForMaterial.objects.filter(contract=contract),
            'object': Object.objects.get(slug=contract.contstruct_object.slug),

        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractAddView(generic.TemplateView):
    template_name = 'appbase/contract/add.html'

    def get(self, request, *args, **kwargs):
        print('asd')
        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        object_id = request.POST['object']
        name = request.POST['name']
        contractor = request.POST['contractor']
        contract = request.FILES['contract']
        number_contract = request.POST['number_contract']
        status = request.POST['status']
        if slugify(name) == None:
            slug = name
        else:
            slug = slugify(name)

        Contract.objects.create(contstruct_object_id=object_id, name=name, slug=slug, contract=contract,
                                contractor=contractor, number_contract=number_contract, status=status)

        return redirect('/objects/' + Object.objects.get(id=object_id).slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractEditView(generic.TemplateView):
    template_name = 'appbase/contract/edit.html'

    def get(self, request, *args, **kwargs):

        contract_slug = self.kwargs['slug']

        contract = Contract.objects.get(slug=contract_slug)
        self.extra_context = {
            'object': Object.objects.get(slug=contract.contstruct_object.slug),
            'contract': contract
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)
        object_id = request.POST['object']
        name = request.POST['name']
        if request.FILES:
            contract_file = request.FILES['contract']
        else:
            contract_file = contract.contract
        contractor = request.POST['contractor']

        number_contract = request.POST['number_contract']
        status = request.POST['status']
        slug = slugify(name)

        contract.name = name
        contract.contract = contractor
        contract.contract = contract_file
        contract.number_contract = number_contract
        contract.status = status
        contract.save()

        return redirect('/objects/' + contract.contstruct_object.slug)


@login_required(login_url='/accounts/login/')
def contract_delete(request):
    contract = Contract.objects.get(id=int(request.POST['contract']))
    red = contract.contstruct_object.slug
    contract.delete()

    return redirect('/objects/' + red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestAddView(generic.TemplateView):
    template_name = 'appbase/contract/request/add.html'

    def get(self, request, *args, **kwargs):
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        self.extra_context = {
            'contract': contract,
            'object': Object.objects.get(contract=contract)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(id=request.POST['contract'])
        name = request.POST['name']
        file = request.FILES['request']
        RequestForMaterial.objects.create(contract=contract, name=name, file=file)
        return redirect('/contract/detail/' + contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestEditView(generic.TemplateView):
    template_name = 'appbase/contract/request/edit.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        self.extra_context = {
            'request_mat': request_mat,
            'object': Object.objects.get(contract__request=request_mat)
        }

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=request.POST['id'])

        # contract_slug = self.kwargs['contract_slug']
        # contract = Contract.objects.get(slug=contract_slug)
        # object_id = request.POST['object']
        name = request.POST['name']
        if request.FILES:
            request_mat_file = request.FILES['request']
        else:
            request_mat_file = request_mat.file

        request_mat.name = name
        request_mat.file = request_mat_file
        request_mat.save()

        return redirect('/contract/detail/' + request_mat.contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestDetailView(generic.TemplateView):
    template_name = 'appbase/contract/request/detail.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])

        self.extra_context = {
            'request_mat': request_mat,
            'object': Object.objects.get(slug=request_mat.contract.contstruct_object.slug),
        }
        return super().get(request, *args, **kwargs)


@login_required(login_url='/accounts/login/')
def request_delete(request):
    request_mat = RequestForMaterial.objects.get(id=request.POST['id'])
    red = '/contract/detail/' + request_mat.contract.slug
    request_mat.delete()

    return redirect(red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceAddView(generic.TemplateView):
    template_name = 'appbase/contract/request/invoice/add.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        self.extra_context = {
            'request_mat': request_mat,
            'object': Object.objects.get(contract__request=request_mat)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=int(request.POST['id']))
        file = request.FILES['invoice']
        InvoiceForPayment.objects.create(request_mat=request_mat, file=file)
        return redirect('/request/detail/' + str(request_mat.id))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceEditView(generic.TemplateView):
    template_name = 'appbase/contract/request/invoice/edit.html'

    def get(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(self.kwargs['id']))

        self.extra_context = {
            'invoice': invoice,
            'object': Object.objects.get(contract__request__invoice=invoice)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
        file = request.FILES['invoice']
        invoice.file = file
        invoice.save()
        return redirect('/request/detail/' + str(invoice.request_mat.id))


@login_required(login_url='/accounts/login/')
def invoice_delete(request):
    invoice = InvoiceForPayment.objects.get(id=request.POST['id'])
    red = '/request/detail/' + str(invoice.request_mat.id)
    invoice.delete()

    return redirect(red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentView(generic.TemplateView):
    template_name = 'appbase/invoices.html'

    def get(self, request, *args, **kwargs):
        con_object = Object.objects.get(slug=self.kwargs['slug'])
        invoices = InvoiceForPayment.objects.filter(status='да', request_mat__contract__contstruct_object=con_object)
        self.extra_context = {
            'object': con_object,
            'invoices': invoices,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['invoice_id']))
        invoice.is_paid = True
        invoice.save()
        return redirect('/invoice_for_payment/' + invoice.request_mat.contract.contstruct_object.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AddMaterialView(generic.TemplateView):
    template_name = 'appbase/contract/add_material.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'object': Object.objects.get(contract__slug=self.kwargs['slug']),
            'contract': Contract.objects.get(slug=self.kwargs['slug']),
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(id=int(request.POST['contract']))
        file = request.FILES['file']
        wb = load_workbook(file)
        sheet_name = wb.sheetnames[0]
        sheet = wb.get_sheet_by_name(sheet_name)
        data = list(sheet.values)
        for item in data:
            name = item[0]
            quantuty = item[1]
            units = item[2]
            price = item[3]
            sum_price = item[4]
            Material.objects.create(contract=contract, name=name, quantity=quantuty, units=units, price=price,
                                    sum_price=sum_price)
        return redirect('/contract/detail/' + contract.slug)
        # return super().get(request, *args, **kwargs)


class PaidMaterailsView(generic.TemplateView):
    template_name = 'appbase/paid_materials.html'

    def get(self, request, *args, **kwargs):
        materails = Material.objects.filter(contract__contstruct_object__slug=self.kwargs['slug'], is_delivery=False)
        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
            # 'contract': Contract.objects.get(slug=self.kwargs['slug']),
            'materials': materails
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        materials = request.POST.getlist('materials')
        for material_id in materials:
            material = Material.objects.get(id=material_id)
            material.is_delivery = True
            material.save()
        return redirect('/objects/' + self.kwargs['slug'] + '/paid_materials')


class MaterialsView(generic.TemplateView):
    template_name = 'appbase/materials.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
            'materials': Material.objects.filter(contract__contstruct_object__slug=self.kwargs['slug'],
                                                 is_delivery=True)
        }
        return super().get(request, *args, **kwargs)


import requests
import telebot
from telebot import types

token = '1318683651:AAH_fhHdb-PGt9kGhSqEOrVXvak3-jFRljk'
channel_id = '-1001342160485'

bot = telebot.TeleBot(token)



def send_telegram(request):

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    key_then = types.InlineKeyboardButton(text='Потом', callback_data='then')
    keyboard.add(key_then)

    invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
    request_mat_file = invoice.request_mat.file
    invoice_file = invoice.file

    msg = '----------------------------------------\n'
    msg += 'Новый счет!\n'
    bot.send_message('438797738', text=msg)
    msg = 'Объект: ' + str(invoice.request_mat.contract.contstruct_object) + '\n'
    msg += 'Работа: ' + str(invoice.request_mat.contract) + '\n'
    msg += 'Текущий статус:: ' + str(invoice.status) + '\n'
    msg += 'ID: ' + str(invoice.id) + '\n'
    bot.send_document('438797738', request_mat_file)
    bot.send_document('438797738', invoice_file)
    bot.send_message('438797738', text=msg, reply_markup=keyboard)
    # requests.get("https://api.telegram.org/bot%s/sendMessage" % token,
    #              params={'chat_id': '438797738', 'text': 'message'})

    return redirect('/request/detail/' + str(invoice.request_mat.id))


def api_telegram_response(request):
    if request.GET['token'] == '123':
        print('asd')
        response = request.GET['response']
        invoice_id = int(request.GET['invoice_id'])
        invoice = InvoiceForPayment.objects.get(id=invoice_id)
        status = '-'
        if response == 'yes':
            status = 'да'
        elif response == 'no':
            status = 'нет'
        elif response == 'then':
            status = 'потом'
        invoice.status = status
        invoice.save()


    return HttpResponse('ok')






