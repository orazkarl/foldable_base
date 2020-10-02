from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from construction_objects_app.models import ConstructionObject
from contracts_app.models import InvoiceForPayment, Contract
from .models import Material
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from openpyxl import load_workbook
import requests
from django.db.models import F, Q
from transliterate import slugify
import telebot
import datetime

import os
from foldable_base.settings import BASE_DIR
from docxtpl import DocxTemplate

GENERAL_BOT_TOKEN = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'
channel_id = '-1001342160485'


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AddMaterialView(generic.TemplateView):
    template_name = 'construction_objects_app/contract/request/invoice/add_material.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__id=self.kwargs['id'])
        invoice = InvoiceForPayment.objects.get(id=self.kwargs['id'])
        if request.user.role == 'accountant' or request.user.role == 'manager' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'construction_object': construction_object,
            'invoice': invoice,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
        object_name = invoice.request_for_material.contract.construction_object.name
        object_name = object_name.split(' ')
        object_slug = ''

        for i in object_name:
            if slugify(i) != None:
                i = slugify(i)
            object_slug += i[0]
        object_slug = object_slug.upper()
        doc_file = request.FILES['doc_file']
        wb = load_workbook(doc_file)
        sheet_name = wb.sheetnames[0]
        sheet = wb.get_sheet_by_name(sheet_name)
        data = list(sheet.values)
        for item in data:
            if item[0] is None:
                continue
            name = item[0]
            quantuty = item[1]
            units = item[2]
            price = item[3]
            sum_price = item[4]
            instriment_code = None
            if len(item) > 5:
                instriment_code = item[5]
            if (isinstance(quantuty, int)) == False:
                quantuty = int(quantuty)
            if (isinstance(price, int)) == False:
                price = int(price)
            sum_price = quantuty * price
            material = Material.objects.create(invoice=invoice, name=name, quantity=quantuty, units=units, price=price,
                                               sum_price=int(sum_price))

            if instriment_code == 1:
                instriment_code = 'I' + object_slug + '-' + str(datetime.datetime.now().year) + '-'
                material.instrument_code = instriment_code + str(material.id)
                material.is_instrument = True
            material.save()

        return redirect('/request_for_material/detail/' + str(invoice.request_for_material.id))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class PaidMaterailsView(generic.TemplateView):
    template_name = 'paid_materials_app/paid_materials/invoices.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        invoices = InvoiceForPayment.objects.filter(
            request_for_material__contract__construction_object=construction_object)

        self.extra_context = {
            'construction_object': construction_object,
            'invoices': invoices,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoicePaidMaterialsView(generic.TemplateView):
    template_name = 'paid_materials_app/paid_materials/paid_materials.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__id=self.kwargs['id'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        materials = Material.objects.filter(invoice__id=int(self.kwargs['id'])).filter(~Q(ok=F('quantity')))
        invoice = InvoiceForPayment.objects.get(id=self.kwargs['id'])

        if list(materials) == [] and list(invoice.material.all()) != []:
            invoice.is_done = True
            invoice.save()

        self.extra_context = {
            'construction_object': construction_object,
            'paid_materials_app': materials,
            'invoice': invoice
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment__id=self.kwargs['id'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        materials = request.POST.getlist('paid_materials_app')
        materials = Material.objects.filter(id__in=materials)
        context = {
            'paid_materials_app': materials,
            'construction_object': construction_object,
        }
        if request.POST['submit'] == 'delivered':
            for material in materials:
                material.is_delivery = True
                material.status = 'ок'
                material.ok = material.quantity
                material.remainder_count = material.quantity
                material.marriage, material.shortage, material.inconsistency = 0, 0, 0
                material.save()
        elif request.POST['submit'] == 'marriage':
            return render(request, template_name='paid_materials_app/paid_materials/marriage_materials.html',
                          context=context)

        elif request.POST['submit'] == 'return':
            return render(request, template_name='paid_materials_app/paid_materials/return_materials.html',
                          context=context)
        return redirect('/construction_objects_app/invoice/' + str(self.kwargs['id']) + '/paid_materials_app')


def marriage_materials(request):
    if request.POST:
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Бракованные товары\n'
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            material.ok = request.POST['ok' + str(i)]
            material.marriage = request.POST['brak' + str(i)]
            material.shortage = request.POST['neso' + str(i)]
            material.inconsistency = request.POST['nexv' + str(i)]
            material.status = 'брак'
            if int(material.marriage) + int(material.ok) + int(material.shortage) + int(
                    material.inconsistency) != material.quantity:
                return HttpResponse('Ошибка!')
            if int(material.ok) > 1:
                material.is_delivery = True
            material.save()

            message += str(
                i) + '. ' + material.name + '\n' + 'Ок: ' + material.ok + '\nБрак: ' + material.marriage + '\nНехватка: ' + material.inconsistency + '\nНесоответсвие: ' + material.shortage + '\n\n'
            invoice = material.invoice
        if request.POST['comment']:
            message += 'Примечение: ' + request.POST['comment'] + '\n'
        construction_object = ConstructionObject.objects.get(contract__request_for_material__invoice_for_payment=invoice)
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        message += 'БИН: ' + invoice.bin + '\n'
        message += 'Название компании: ' + invoice.name_company + '\n'
        requests.get("https://api.telegram.org/bot%s/sendMessage" % GENERAL_BOT_TOKEN,
                     params={'chat_id': '-1001342160485', 'text': message})
        bot = telebot.TeleBot(GENERAL_BOT_TOKEN)
        bot.send_document(channel_id, invoice.doc_file)
    return redirect(request.META.get('HTTP_REFERER'))


def return_materials(request):
    if request.POST:
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Возврат товаров\n'
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            return_materials_count = int(request.POST['return' + str(i)])
            invoice = material.invoice
            if return_materials_count > material.quantity:
                return HttpResponse('Ошибка!')
            elif return_materials_count == material.quantity:
                material.delete()
            else:
                material.quantity = material.quantity - return_materials_count
                material.marriage, material.shortage, material.inconsistency = 0, 0, 0
                material.ok = material.quantity
                material.remainder_count = material.quantity
                material.status = 'ок'
                material.save()
            message += str(i) + '. ' + material.name + '\n' + 'Количество: ' + str(
                material.quantity) + '\nКоличество возвратных товаров: ' + str(return_materials_count) + '\n\n'
        if request.POST['comment']:
            message += 'Примечение: ' + request.POST['comment']
        construction_object = ConstructionObject.objects.get(
            contract__request_for_material__invoice_for_payment=invoice)
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        message += 'БИН: ' + str(invoice.bin) + '\n'
        message += 'Название компании: ' + invoice.name_company + '\n'
        requests.get("https://api.telegram.org/bot%s/sendMessage" % GENERAL_BOT_TOKEN,
                     params={'chat_id': '-1001342160485', 'text': message})
        bot = telebot.TeleBot(GENERAL_BOT_TOKEN)
        bot.send_document(channel_id, invoice.doc_file)
    return redirect(request.META.get('HTTP_REFERER'))


