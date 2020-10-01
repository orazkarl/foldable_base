from django.shortcuts import render, redirect, HttpResponse
from django.views import generic
from .models import ConstructionObject, Contract, RequestForMaterial, InvoiceForPayment
from material_app.views import Material
from transliterate import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime
import telebot
from telebot import types

GENERAL_BOT_TOKEN = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'
general_bot = telebot.TeleBot(GENERAL_BOT_TOKEN)
channel_id = '-1001342160485'


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
        construction_object = contract.construction_object
        requests_for_materirals = RequestForMaterial.objects.filter(contract=contract)
        if request.user.role == 'accountant' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        for request_for_material in requests_for_materirals:
            if all(invoice.is_done == True for invoice in request_for_material.invoice_for_payment.all()) and list(
                    request_for_material.invoice_for_payment.all()) != []:
                request_for_material.is_done = True
                request_for_material.save()
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
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        construction_object_id = request.POST['construction_object']
        name = request.POST['name_contract']
        contractor = request.POST['contractor']
        doc_file = request.FILES['doc_file_contract']
        number_contract = request.POST['number_contract']
        status = request.POST['status_contract']
        bin = request.POST['bin_contract']
        date_contract = request.POST['date_contract']
        if slugify(name) == None:
            slug = name
        else:
            slug = slugify(name)

        Contract.objects.create(construction_object_id=construction_object_id, name=name, slug=slug,
                                contract_file=doc_file,
                                contractor=contractor, number_contract=number_contract, status=status,
                                date_contract=date_contract, bin=bin)

        return redirect(
            '/construction_objects/' + ConstructionObject.objects.get(id=construction_object_id).slug + '/' + str(
                status))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractEditView(generic.TemplateView):
    template_name = 'construction_objects/contract/edit.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'contract': contract
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        construction_object_id = request.POST['construction_object']
        name = request.POST['name_contract']
        contractor = request.POST['contractor']
        number_contract = request.POST['number_contract']
        status = request.POST['status_contract']
        bin = request.POST['bin_contract']
        date_contract = request.POST['date_contract']
        slug = slugify(name)
        if request.FILES:
            contract_file = request.FILES['doc_file_contract']
        else:
            contract_file = contract.contract_file

        contract.name = name
        contract.contract = contractor
        contract.contract_file = contract_file
        contract.number_contract = number_contract
        contract.status = status
        contract.bin = bin
        contract.date_contract = date_contract
        contract.save()

        return redirect(
            '/construction_objects/' + ConstructionObject.objects.get(id=construction_object_id).slug + '/' + str(
                status))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialAddView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/add.html'

    def get(self, request, *args, **kwargs):
        contract = Contract.objects.get(slug=self.kwargs['slug'])
        construction_object = ConstructionObject.objects.get(contract=contract)
        if request.user.role == 'accountant' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'contract': contract,
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(id=request.POST['contract'])
        name = request.POST['name']
        doc_file = request.FILES['doc_file']
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Новая заявка!\n'
        message += 'Работа: ' + contract.name + '\n'
        general_bot.send_message(channel_id, text=message)
        general_bot.send_document(channel_id, doc_file)
        RequestForMaterial.objects.create(contract=contract, name=name, doc_file=doc_file, is_done=False)

        return redirect('/contract/detail/' + contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialEditView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/edit.html'

    def get(self, request, *args, **kwargs):
        request_for_material = RequestForMaterial.objects.get(id=self.kwargs['id'])
        construction_object = ConstructionObject.objects.get(contract__request_for_material=request_for_material)
        if request.user.role == 'accountant' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'request_for_material': request_for_material,
            'construction_object': construction_object,
        }

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_for_material = RequestForMaterial.objects.get(id=request.POST['id'])

        name = request.POST['name']
        if request.FILES:
            doc_file = request.FILES['doc_file']
        else:
            doc_file = request_for_material.doc_file

        request_for_material.name = name
        request_for_material.doc_file = doc_file
        request_for_material.save()

        return redirect('/contract/detail/' + request_for_material.contract.slug)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RequestForMaterialDetailView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/detail.html'

    def get(self, request, *args, **kwargs):
        request_for_material = RequestForMaterial.objects.get(id=self.kwargs['id'])
        construction_object = ConstructionObject.objects.get(contract__request_for_material=request_for_material)
        if request.user.role == 'accountant' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        # if all(invoice.is_done == True for invoice in request_for_material.invoice_for_payment.all()) and list(request_for_material.invoice_for_payment.all()) != []:
        #     request_for_material.is_done = True
        #     request_for_material.save()

        self.extra_context = {
            'request_for_material': request_for_material,
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentAddView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/invoice/add.html'

    def get(self, request, *args, **kwargs):
        request_for_material = RequestForMaterial.objects.get(id=self.kwargs['id'])
        construction_object = ConstructionObject.objects.get(contract__request_for_material=request_for_material)
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'request_for_material': request_for_material,
            'construction_object': construction_object,
            'invoices': InvoiceForPayment.objects.all().values_list('bin', 'name_company').distinct(),
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, id):
        request_for_material = RequestForMaterial.objects.get(pk=int(request.POST['request_for_material_id']))
        doc_file = request.FILES['doc_file_invoice']
        bin = request.POST['bin_invoice']
        name_company = request.POST['name_invoice']
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

        InvoiceForPayment.objects.create(request_for_material=request_for_material, doc_file=doc_file, bin=bin,
                                         name_company=name_company, comment=comment, is_cash=is_cash, is_paid=is_paid,
                                         is_looked=is_looked,
                                         status=status)
        return redirect('/request_for_material/detail/' + str(request_for_material.id))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentEditView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/invoice/edit.html'

    def get(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(self.kwargs['id']))
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment=invoice)
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'invoice': invoice,
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
        if request.FILES:
            doc_file = request.FILES['doc_file']
        else:
            doc_file = invoice.doc_file
        invoice.doc_file = doc_file
        invoice.bin = request.POST['bin']
        invoice.name_company = request.POST['name']
        invoice.comment = request.POST['comment']
        is_cash = ''
        if 'is_cash' in request.POST:
            is_cash = request.POST['is_cash']
        if is_cash == 'on':
            invoice.is_cash = True
        else:
            invoice.is_cash = False
        invoice.save()
        return redirect('/request_for_material/detail/' + str(invoice.request_for_material.id))


@login_required(login_url='/accounts/login/')
def invoice_delete(request):
    invoice = InvoiceForPayment.objects.get(id=request.POST['id'])
    construction_object = ConstructionObject.objects.get(contract__request_for_material__invoice_for_payment=invoice)
    if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
            request.user.construction_objects.all()):
        return render(request, template_name='404.html')
    red = '/request_for_material/detail/' + str(invoice.request_for_material.id)
    invoice.delete()
    return redirect(red)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentDetailView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/invoice/detail.html'

    def get(self, request, *args, **kwargs):
        invoice_for_payment = InvoiceForPayment.objects.get(id=int(self.kwargs['id']))
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment=invoice_for_payment)
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        materials = Material.objects.filter(invoice=invoice_for_payment, invoice__is_done=False)

        self.extra_context = {
            'construction_object': construction_object,
            'invoice': invoice_for_payment,
            'materials': materials

        }

        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class MaterialAddView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/invoice/material/add.html'

    def get(self, request, *args, **kwargs):
        invoice_for_payment = InvoiceForPayment.objects.get(id=int(self.kwargs['id']))
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment=invoice_for_payment)
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'invoice': invoice_for_payment,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        invoice = InvoiceForPayment.objects.get(pk=int(request.POST['invoice_id']))
        object_name = invoice.request_for_material.contract.construction_object.name
        object_name = object_name.split(' ')
        object_slug = ''
        for i in object_name:
            if slugify(i) != None:
                i = slugify(i)
            object_slug += i[0]
        object_slug = object_slug.upper()

        name = request.POST['name']
        quantity = int(request.POST['quantity'])
        units = request.POST['units']
        price = int(request.POST['price'])
        sum_price = int(request.POST['sum_price'])
        is_instrument = 'off'

        if 'is_instrument' in request.POST:
            is_instrument = request.POST['is_instrument']
        if is_instrument == 'on':
            is_instrument = True
        else:
            is_instrument = False
        material = Material.objects.create(invoice=invoice, name=name, quantity=quantity, units=units, price=price,
                                           sum_price=sum_price)
        if is_instrument:
            instriment_code = 'I' + object_slug + '-' + str(datetime.datetime.now().year) + '-'
            material.instrument_code = instriment_code + str(material.id)
            material.is_instrument = True
            material.save()

        return redirect('/invoice/detail/' + str(invoice.id))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class MaterialEditView(generic.TemplateView):
    template_name = 'construction_objects/contract/request/invoice/material/edit.html'

    def get(self, request, *args, **kwargs):
        material = Material.objects.get(id=int(self.kwargs['id']))
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__material=material)
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'material': material
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        material = Material.objects.get(pk=int(request.POST['material_id']))
        object_name = material.invoice.request_for_material.contract.construction_object.name
        object_name = object_name.split(' ')
        object_slug = ''
        for i in object_name:
            if slugify(i) != None:
                i = slugify(i)
            object_slug += i[0]
        object_slug = object_slug.upper()

        name = request.POST['name']
        quantity = int(request.POST['quantity'])
        units = request.POST['units']
        price = int(request.POST['price'])
        sum_price = int(request.POST['sum_price'])
        is_instrument = 'off'
        if 'is_instrument' in request.POST:
            is_instrument = request.POST['is_instrument']
        if is_instrument == 'on':
            is_instrument = True
        else:
            is_instrument = False
        material.name = name
        material.quantity = quantity
        material.units = units
        material.price = price
        material.sum_price = sum_price
        if is_instrument:
            instriment_code = 'I' + object_slug + '-' + str(datetime.datetime.now().year) + '-'
            material.instrument_code = instriment_code + str(material.id)
            material.is_instrument = True
        else:
            material.is_instrument = False
            material.instrument_code = None
        material.save()

        return redirect('/invoice/detail/' + str(material.invoice.id))

@login_required(login_url='/accounts/login/')
def material_delete(request):
    material = Material.objects.get(id=int(request.POST['material_id']))
    invoice = material.invoice
    construction_object = invoice.request_for_material.contract.construction_object
    if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(request.user.construction_objects.all()):
        return render(request, template_name='404.html')
    red = '/invoice/detail/' + str(invoice.id)
    material.delete()
    return redirect(red)

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoiceForPaymentView(generic.TemplateView):
    template_name = 'construction_objects/invoices.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'manager' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        invoices = InvoiceForPayment.objects.filter(status='да',
                                                    request_for_material__contract__construction_object=construction_object)

        self.extra_context = {
            'construction_object': construction_object,
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
            general_bot.send_document(channel_id, invoice.doc_file)
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
            general_bot.send_document(channel_id, invoice.doc_file)
            invoice.save()
            invoice.save()
        return redirect('/invoice_for_payment/' + invoice.request_for_material.contract.construction_object.slug)


token = '1318683651:AAH_fhHdb-PGt9kGhSqEOrVXvak3-jFRljk'


def send_telegram(request):
    bot = telebot.TeleBot(token)
    invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
    construction_object = ConstructionObject.objects.get(contract__request_for_material__invoice_for_payment=invoice)
    if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
            request.user.construction_objects.all()):
        return render(request, template_name='404.html')
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    key_then = types.InlineKeyboardButton(text='Потом', callback_data='then')
    keyboard.add(key_then)

    request_for_material_file = invoice.request_for_material.doc_file
    invoice_file = invoice.doc_file
    msg = '\n\n\n'
    msg += '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
    msg += 'Новый счет!\n'
    bot.send_message('438797738', text=msg)
    msg = 'Объект: ' + str(invoice.request_for_material.contract.construction_object) + '\n'
    msg += 'Работа: ' + str(invoice.request_for_material.contract) + '\n'
    msg += 'Текущий статус: ' + str(invoice.status) + '\n'
    bot.send_message('438797738', text=msg)

    bot.send_document('438797738', request_for_material_file)
    bot.send_document('438797738', invoice_file)
    msg = 'ID: ' + str(invoice.id) + '\n'
    bot.send_message('438797738', text=msg, reply_markup=keyboard)

    return redirect('/request_for_material/detail/' + str(invoice.request_for_material.id))


def api_telegram_response(request):
    message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
    message += 'Счет на оплату!' + '\n'
    bot = telebot.TeleBot(GENERAL_BOT_TOKEN)

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
        bot.send_document(channel_id, invoice.request_for_material.doc_file)
        bot.send_document(channel_id, invoice.doc_file)

    return HttpResponse('ok')
