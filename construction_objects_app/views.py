from django.shortcuts import render, redirect, HttpResponse
from django.views import generic
from .models import ConstructionObject, Contract, RequestForMaterial, InvoiceForPayment
from transliterate import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime
import requests

import telebot
from telebot import types

GENERAL_BOT_TOKEN = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'
general_bot = telebot.TeleBot(GENERAL_BOT_TOKEN)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class HomeView(generic.ListView):
    template_name = 'index.html'
    queryset = ConstructionObject.objects.all()


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ConstructionObjectDetailView(generic.TemplateView):
    template_name = 'construction_objects/object_detail.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if construction_object not in list(request.user.construction_objects.all()):
            return render(request, '404.html')
        if request.user.role == 'accountant':
            return redirect('/invoice_for_payment/' + construction_object.slug)
        contracts = Contract.objects.filter(construction_object=construction_object, status=str(self.kwargs['pk']))

        self.extra_context = {
            'contracts': contracts,
            'construction_object': construction_object
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractDetailView(generic.TemplateView):
    template_name = 'construction_objects/contract/detail.html'

    def get(self, request, *args, **kwargs):
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        construction_object = contract.contstruct_object
        requests_for_materirals = RequestForMaterial.objects.filter(contract=contract)
        if request.user.role == 'accountant' or construction_object not in list(request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'contract': contract,
            'requests_for_materirals': requests_for_materirals,
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractAddView(generic.TemplateView):
    template_name = 'construction_objects/contract/add.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        object_id = request.POST['object']
        name = request.POST['name']
        contractor = request.POST['contractor']
        contract = request.FILES['contract']
        number_contract = request.POST['number_contract']
        status = request.POST['status']
        bin = request.POST['bin']
        date_contract = request.POST['date_contract']
        if slugify(name) == None:
            slug = name
        else:
            slug = slugify(name)

        Contract.objects.create(contstruct_object_id=object_id, name=name, slug=slug, contract=contract,
                                contractor=contractor, number_contract=number_contract, status=status,
                                date_contract=date_contract, bin=bin)

        return redirect('/objects/' + ConstructionObject.objects.get(id=object_id).slug + '/' + str(status))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractEditView(generic.TemplateView):
    template_name = 'appbase/../templates/construction_objects/contract/edit.html'

    def get(self, request, *args, **kwargs):
        contract_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)
        if request.user.role == 'accountant' or request.user.role == 'manager' or ConstructionObject.objects.get(
                slug=contract.contstruct_object.slug) not in list(request.user.object.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'object': ConstructionObject.objects.get(slug=contract.contstruct_object.slug),
            'contract': contract
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract_slug = self.kwargs['slug']
        contract = Contract.objects.get(slug=contract_slug)
        object_id = request.POST['object']
        name = request.POST['name']

        contractor = request.POST['contractor']

        number_contract = request.POST['number_contract']
        status = request.POST['status']
        bin = request.POST['bin']
        date_contract = request.POST['date_contract']
        slug = slugify(name)
        if request.FILES:
            contract_file = request.FILES['contract']
        else:
            contract_file = contract.contract

        contract.name = name
        contract.contract = contractor
        contract.contract = contract_file
        contract.number_contract = number_contract
        contract.status = status
        contract.bin = bin
        contract.date_contract = date_contract
        contract.save()

        return redirect(
            '/objects/' + ConstructionObject.objects.get(id=object_id).slug + '/' + str(status_dict[status]))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestAddView(generic.TemplateView):
    template_name = 'appbase/../templates/construction_objects/contract/request/add.html'

    def get(self, request, *args, **kwargs):
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or ConstructionObject.objects.get(contract=contract) not in list(
                request.user.object.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'contract': contract,
            'object': ConstructionObject.objects.get(contract=contract)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(id=request.POST['contract'])
        name = request.POST['name']
        file = request.FILES['request']
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Новая заявка!\n'
        message += 'Работа: ' + contract.name + '\n'
        general_bot.send_message(channel_id, text=message)
        general_bot.send_document(channel_id, file)
        RequestForMaterial.objects.create(contract=contract, name=name, file=file, is_done=False)

        return redirect('/contract/detail/' + contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestEditView(generic.TemplateView):
    template_name = 'appbase/../templates/construction_objects/contract/request/edit.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        if request.user.role == 'accountant' or ConstructionObject.objects.get(
                contract__request=request_mat) not in list(
            request.user.object.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'request_mat': request_mat,
            'object': ConstructionObject.objects.get(contract__request=request_mat)
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
    template_name = 'appbase/../templates/construction_objects/contract/request/detail.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        if request.user.role == 'accountant' or ConstructionObject.objects.get(
                contract__request=request_mat) not in list(
            request.user.object.all()):
            return render(request, template_name='404.html')

        if all(invoice.is_done == True for invoice in request_mat.invoice.all()) and list(
                request_mat.invoice.all()) != []:
            request_mat.is_done = True
            request_mat.save()

        self.extra_context = {
            'request_mat': request_mat,
            'object': ConstructionObject.objects.get(contract__request=request_mat),
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceAddView(generic.TemplateView):
    template_name = 'appbase/../templates/construction_objects/contract/request/invoice/add.html'

    def get(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=self.kwargs['id'])
        if request.user.role == 'accountant' or request.user.role == 'manager' or ConstructionObject.objects.get(
                contract__request=request_mat) not in list(request.user.object.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'request_mat': request_mat,
            'object': ConstructionObject.objects.get(contract__request=request_mat)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_mat = RequestForMaterial.objects.get(id=int(request.POST['id']))
        file = request.FILES['invoice']
        bin = request.POST['bin']
        name_company = request.POST['name']
        comment = request.POST['comment']
        is_cash = 'off'
        if 'is_cash' in request.POST:
            is_cash = request.POST['is_cash']
        is_paid, is_looked = False, False
        status = '-'
        if is_cash == 'on':
            is_cash, is_paid, is_looked = True, True, True
            status = 'да'
        else:
            is_cash = False
        InvoiceForPayment.objects.create(request_mat=request_mat, file=file, bin=bin, name_company=name_company,
                                         comment=comment, is_cash=is_cash, is_paid=is_paid, is_looked=is_looked,
                                         status=status)
        return redirect('/request/detail/' + str(request_mat.id))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceEditView(generic.TemplateView):
    template_name = 'appbase/../templates/construction_objects/contract/request/invoice/edit.html'

    def get(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(self.kwargs['id']))
        if request.user.role == 'accountant' or request.user.role == 'manager' or ConstructionObject.objects.get(
                contract__request__invoice=invoice) not in list(request.user.object.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'invoice': invoice,
            'object': ConstructionObject.objects.get(contract__request__invoice=invoice)
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
        if request.FILES:
            file = request.FILES['file']
        else:
            file = invoice.file
        invoice.file = file
        invoice.bin = request.POST['bin']
        invoice.name_company = request.POST['name']
        invoice.comment = request.POST['comment']
        is_cash = request.POST['is_cash']
        if is_cash == 'on':
            invoice.is_cash = True
        else:
            invoice.is_cash = False
        invoice.save()
        return redirect('/request/detail/' + str(invoice.request_mat.id))


@login_required(login_url='/accounts/login/')
def invoice_delete(request):
    invoice = InvoiceForPayment.objects.get(id=request.POST['id'])
    if request.user.role == 'accountant' or request.user.role == 'manager' or ConstructionObject.objects.get(
            contract__request__invoice=invoice) not in list(request.user.object.all()):
        return render(request, template_name='404.html')

    red = '/request/detail/' + str(invoice.request_mat.id)
    invoice.delete()

    return redirect(red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentView(generic.TemplateView):
    template_name = 'appbase/../templates/construction_objects/invoices.html'

    def get(self, request, *args, **kwargs):
        con_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'manager' or request.user.role == 'purchaser' or con_object not in list(
                request.user.object.all()):
            return render(request, template_name='404.html')

        invoices = InvoiceForPayment.objects.filter(status='да', request_mat__contract__contstruct_object=con_object)

        self.extra_context = {
            'object': con_object,
            'invoices': invoices,
            'current_date': datetime.datetime.now()

        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['invoice_id']))

        if request.POST['submit'] == 'paid':
            invoice.is_paid = True
            invoice.reset_date = datetime.datetime.now() + datetime.timedelta(minutes=30)
            message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
            message += 'Счет оплачен!\n'
            message += 'БИН: ' + invoice.bin + '\n'
            general_bot.send_message(channel_id, message)
            general_bot.send_document(channel_id, invoice.file)
            invoice.save()

        elif request.POST['submit'] == 'looked':
            invoice.is_looked = True
            invoice.save()
        elif request.POST['submit'] == 'cancel':
            invoice.is_looked = False
            invoice.is_paid = False
            message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
            message += 'Оплаченный счет отменен!\n'
            message += 'БИН: ' + invoice.bin + '\n'
            general_bot.send_message(channel_id, message)
            general_bot.send_document(channel_id, invoice.file)
            invoice.save()
            invoice.save()
        return redirect('/invoice_for_payment/' + invoice.request_mat.contract.contstruct_object.slug)


token = '1318683651:AAH_fhHdb-PGt9kGhSqEOrVXvak3-jFRljk'

channel_id = '-1001342160485'

bot = telebot.TeleBot(token)


def send_telegram(request):
    invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
    if request.user.role == 'accountant' or request.user.role == 'manager' or ConstructionObject.objects.get(
            contract__request__invoice=invoice) not in list(request.user.object.all()):
        return render(request, template_name='404.html')
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    key_then = types.InlineKeyboardButton(text='Потом', callback_data='then')
    keyboard.add(key_then)

    request_mat_file = invoice.request_mat.file
    invoice_file = invoice.file
    msg = '\n\n\n'
    msg += '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
    msg += 'Новый счет!\n'
    bot.send_message('438797738', text=msg)
    msg = 'Объект: ' + str(invoice.request_mat.contract.contstruct_object) + '\n'
    msg += 'Работа: ' + str(invoice.request_mat.contract) + '\n'
    msg += 'Текущий статус: ' + str(invoice.status) + '\n'
    bot.send_message('438797738', text=msg)

    bot.send_document('438797738', request_mat_file)
    bot.send_document('438797738', invoice_file)
    msg = 'ID: ' + str(invoice.id) + '\n'
    bot.send_message('438797738', text=msg, reply_markup=keyboard)

    return redirect('/request/detail/' + str(invoice.request_mat.id))


def api_telegram_response(request):
    if request.user.role == 'accountant' or request.user.role == 'manager':
        return render(request, template_name='404.html')
    message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
    message += 'Счет на оплату!' + '\n'
    bot = telebot.TeleBot(general_bot_token)

    if request.GET['token'] == '123':
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
        message += 'Ответ: ' + status
        bot.send_message(channel_id, text=message)
        bot.send_document(channel_id, invoice.request_mat.file)
        bot.send_document(channel_id, invoice.file)

    # requests.get("https://api.telegram.org/bot%s/sendMessage" % general_bot_token,
    #              params={'chat_id': '-1001302242759', 'text': message})
    return HttpResponse('ok')