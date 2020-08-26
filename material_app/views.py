from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views import generic
from appbase.models import Object, InvoiceForPayment, Contract
from .models import Material, ReleaseMaterial, ReleaseMaterialItem
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from openpyxl import load_workbook
import requests
from django.db.models import F, Q
from transliterate import slugify
import telebot
import datetime

general_bot_token = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'
channel_id = '-1001342160485'


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AddMaterialView(generic.TemplateView):
    template_name = 'appbase/contract/request/invoice/add_material.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'object': Object.objects.get(contract__request__invoice__id=self.kwargs['id']),
            # 'contract': Contract.objects.get(slug=self.kwargs['slug']),
            # 'request_mat': RequestForMaterial.objects.get(id=self.kwargs['id'])
            'invoice': InvoiceForPayment.objects.get(id=self.kwargs['id'])
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # contract = Contract.objects.get(id=int(request.POST['contract']))
        invoice = InvoiceForPayment.objects.get(id=int(request.POST['id']))
        object_name = invoice.request_mat.contract.contstruct_object.name
        # object_name = slugify(object_name)
        object_name = object_name.split(' ')
        object_slug = ''

        for i in object_name:
            if slugify(i) != None:
                i = slugify(i)
            object_slug += i[0]
        #
        object_slug = object_slug.upper()
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
            instriment_code = None
            if len(item) > 5:
                instriment_code = item[5]

            material = Material.objects.create(invoice=invoice, name=name, quantity=quantuty, units=units, price=price,
                                               sum_price=sum_price)

            if instriment_code == 1:
                instriment_code = 'I' + object_slug + '-' + str(datetime.datetime.now().year) + '-'
                material.instrument_code = instriment_code + str(material.id)
            material.save()

        return redirect('/request/detail/' + str(invoice.request_mat.id))
        # return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class PaidMaterailsView(generic.TemplateView):
    template_name = 'appbase/material/paid_materials/invoices.html'

    def get(self, request, *args, **kwargs):
        # materails = Material.objects.filter(request_mat__contract__contstruct_object__slug=self.kwargs['slug'],
        #                                     is_delivery=False)
        invoices = InvoiceForPayment.objects.filter(request_mat__contract__contstruct_object__slug=self.kwargs['slug'])

        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
            'invoices': invoices,

            # 'materials': materails
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InvoicePaidMaterialsView(generic.TemplateView):
    template_name = 'appbase/material/paid_materials/paid_materials.html'

    def get(self, request, *args, **kwargs):
        materials = Material.objects.filter(invoice__id=int(self.kwargs['id'])).filter(~Q(ok=F('quantity')))
        invoice = InvoiceForPayment.objects.get(id=self.kwargs['id'])

        if list(materials) == [] and list(invoice.material.all()) != []:
            invoice.is_done = True
            invoice.save()

        self.extra_context = {
            'object': Object.objects.get(contract__request__invoice__id=self.kwargs['id']),
            'materials': materials,
            'invoice': invoice
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        materials = request.POST.getlist('materials')
        materials = Material.objects.filter(id__in=materials)
        context = {
            'materials': materials,
            'object': Object.objects.get(contract__request__invoice__id=self.kwargs['id']),
        }
        if request.POST['submit'] == 'delivered':
            for material in materials:
                material.is_delivery = True
                material.status = 'ок'
                material.ok = material.quantity
                material.brak, material.nesotvetsvie, material.nexvatka = 0, 0, 0
                material.save()
        elif request.POST['submit'] == 'marriage':
            return render(request, template_name='appbase/material/paid_materials/marriage_materials.html',
                          context=context)

        elif request.POST['submit'] == 'return':
            return render(request, template_name='appbase/material/paid_materials/return_materials.html',
                          context=context)
        return redirect('/objects/invoice/' + str(self.kwargs['id']) + '/materials')


def marriage_materials(request):
    if request.POST:
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Бракованные товары\n'
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            material.ok = request.POST['ok' + str(i)]
            material.brak = request.POST['brak' + str(i)]
            material.nesotvetsvie = request.POST['neso' + str(i)]
            material.nexvatka = request.POST['nexv' + str(i)]
            material.status = 'брак'
            if int(material.nesotvetsvie) + int(material.ok) + int(material.brak) + int(
                    material.nexvatka) != material.quantity:
                return HttpResponse('Ошибка!')
            if int(material.ok) > 1:
                material.is_delivery = True
            material.save()

            message += str(
                i) + '. ' + material.name + '\n' + 'Ок: ' + material.ok + '\nБрак: ' + material.brak + '\nНехватка: ' + material.nexvatka + '\nНесоответсвие: ' + material.nesotvetsvie + '\n\n'
            invoice = material.invoice
        if request.POST['comment']:
            message += 'Примечение: ' + request.POST['comment'] + '\n'
        message += 'БИН: ' + invoice.bin + '\n'
        message += 'Название компании: ' + invoice.name_company + '\n'
        requests.get("https://api.telegram.org/bot%s/sendMessage" % general_bot_token,
                     params={'chat_id': '-1001342160485', 'text': message})
        bot = telebot.TeleBot(general_bot_token)
        bot.send_document(channel_id, invoice.file)
    return redirect(request.META.get('HTTP_REFERER'))


def return_materials(request):
    if request.POST:
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Возврат товаров\n'
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            return_mat_count = int(request.POST['return' + str(i)])
            invoice = material.invoice
            if return_mat_count > material.quantity:
                return HttpResponse('Ошибка!')
            elif return_mat_count == material.quantity:
                material.delete()
            else:
                material.quantity = material.quantity - return_mat_count
                material.brak, material.nesotvetsvie, material.nexvatka = 0, 0, 0
                material.ok = material.quantity
                material.status = 'ок'
                material.save()
            message += str(i) + '. ' + material.name + '\n' + 'Количество: ' + str(
                material.quantity) + '\nКоличество возвратных товаров: ' + str(return_mat_count) + '\n\n'
        if request.POST['comment']:
            message += 'Примечение: ' + request.POST['comment']
        message += 'БИН: ' + str(invoice.bin) + '\n'
        message += 'Название компании: ' + invoice.name_company + '\n'
        requests.get("https://api.telegram.org/bot%s/sendMessage" % general_bot_token,
                     params={'chat_id': '-1001342160485', 'text': message})
        bot = telebot.TeleBot(general_bot_token)
        bot.send_document(channel_id, invoice.file)
    return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractMaterialsView(generic.TemplateView):
    template_name = 'appbase/material/store_mateials/contracts.html'

    def get(self, request, *args, **kwargs):
        contracts = Contract.objects.filter(contstruct_object__slug=self.kwargs['slug'])
        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
            'contracts': contracts
            # 'materials': Material.objects.filter(invoice__request_mat__contract__contstruct_object__slug=self.kwargs['slug'], is_delivery=True)
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class MaterialsView(generic.TemplateView):
    template_name = 'appbase/material/store_mateials/materials.html'

    def get(self, request, *args, **kwargs):
        materials = Material.objects.filter(invoice__request_mat__contract__slug=self.kwargs['slug'], is_delivery=True,
                                            invoice__is_done=True)
        self.extra_context = {
            'object': Object.objects.get(contract__slug=self.kwargs['slug']),
            'materials': materials
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        materials = request.POST.getlist('materials')
        materials = Material.objects.filter(id__in=materials)
        for material in materials:
            print(material)
        context = {
            'materials': materials,
            'object': Object.objects.get(contract__slug=self.kwargs['slug']),
        }
        return render(request, template_name='appbase/material/store_mateials/release_materials.html',
                      context=context)

        # return redirect(request.META.get('HTTP_REFERER'))

import os
import io
from foldable_base.settings import BASE_DIR
from docxtpl import DocxTemplate



def release_materials(request):
    if request.POST:
        contract = Material.objects.get(id=int(request.POST['material1'])).invoice.request_mat.contract
        release_mat = ReleaseMaterial.objects.create(user=request.user, release_date=datetime.datetime.now(),
                                                     contract=contract)
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            release_mat_count = int(request.POST['release' + str(i)])
            material.release_count = material.release_count + release_mat_count
            material.save()
            ReleaseMaterialItem.objects.create(release_material=release_mat, material=material,
                                               release_count=release_mat_count)
        indexs = list(range(1, ReleaseMaterialItem.objects.filter(release_material=release_mat).count() + 1))
        context = {
            'object_name': Object.objects.get(contract=contract).name,
            'object_address': Object.objects.get(contract=contract).address,
            'number_contract': contract.number_contract,
            'date_contract': contract.date_contract,
            'date_doc': datetime.datetime.now().date(),
            'role': request.user.role,
            'name': request.user.first_name + ' ' + request.user.last_name,
            'contract_contractor': contract.contractor,
            'materials': ReleaseMaterialItem.objects.filter(release_material=release_mat),
            'indexs': indexs

        }

        byte_io = io.BytesIO()
        tpl = DocxTemplate(os.path.join(BASE_DIR, 'mediafiles/nakladnaya1.docx'))
        tpl.render(context)
        tpl.save(byte_io)
        byte_io.seek(0)
        return FileResponse(byte_io, as_attachment=True,
                            filename=f'nakladnaya1{contract.name}{str(release_mat.id)}.docx')

        # except:
        #     return HttpResponse('Ошибка')

    return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ReleaseMaterialsView(generic.TemplateView):
    template_name = 'appbase/material/store_mateials/relesed_materials_list.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'object': Object.objects.get(contract__slug=self.kwargs['slug']),
            'relesed_materials': ReleaseMaterial.objects.filter(contract__slug=self.kwargs['slug'])
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class DetailReleaseMaterialsView(generic.TemplateView):
    template_name = 'appbase/material/store_mateials/detail_release_mat.html'

    def get(self, request, *args, **kwargs):
        release_mat = ReleaseMaterial.objects.get(id=int(self.kwargs['id']))

        self.extra_context = {
            'object': release_mat.contract.contstruct_object,
            'release_mat' : release_mat,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(realeas_material__id=int(self.kwargs['id']))
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))

            return_mat = request.POST['return_mat' + str(i)]
            material.release_count = material.release_count - int(return_mat)
            material.save()
        return redirect('/contract/' + contract.slug+ '/materials')
        # return redirect('/detail/relesed_materials/' + str(self.kwargs['id']))

