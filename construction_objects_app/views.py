from django.shortcuts import render, redirect, HttpResponse
from django.views import generic
from .models import ConstructionObject
from contracts_app.models import Contract, InvoiceForPayment
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
    template_name = 'construction_objects_app/index.html'
    queryset = ConstructionObject.objects.all()


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ConstructionObjectDetailView(generic.TemplateView):
    template_name = 'construction_objects_app/object_detail.html'

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
class InvoiceForPaymentView(generic.TemplateView):
    template_name = 'construction_objects_app/invoices.html'

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

    return redirect('/request/' + str(invoice.request_for_material.id) + '/detail/')


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
