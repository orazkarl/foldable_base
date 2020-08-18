from django.shortcuts import render, redirect, HttpResponse
from django.views import generic
from appbase.models import Object, InvoiceForPayment
from .models import Material
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from openpyxl import load_workbook
import requests
from django.db.models import F, Q

general_bot_token = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'


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
            Material.objects.create(invoice=invoice, name=name, quantity=quantuty, units=units, price=price,
                                    sum_price=sum_price)

        return redirect('/request/detail/' + str(invoice.request_mat.id))
        # return super().get(request, *args, **kwargs)


class PaidMaterailsView(generic.TemplateView):
    template_name = 'appbase/material/invoices.html'

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


class InvoicePaidMaterialsView(generic.TemplateView):
    template_name = 'appbase/material/paid_materials.html'

    def get(self, request, *args, **kwargs):
        materials = Material.objects.filter(invoice__id=int(self.kwargs['id'])).filter(~Q(ok=F('quantity')))
        self.extra_context = {
            'object': Object.objects.get(contract__request__invoice__id=self.kwargs['id']),
            'materials': materials,
            'invoice': InvoiceForPayment.objects.get(id=self.kwargs['id']),
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
                material.save()
        elif request.POST['submit'] == 'marriage':
            return render(request, template_name='appbase/material/marriage_materials.html', context=context)

        elif request.POST['submit'] == 'return':
            return render(request, template_name='appbase/material/return_materials.html', context=context)
        return redirect('/objects/invoice/' + str(self.kwargs['id']) + '/materials')


def marriage_materials(request):
    if request.POST:
        message = 'Бракованные товары\n'
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
        if 'comment' in request.POST:
            message += 'Примечение: ' + request.POST['comment']
        requests.get("https://api.telegram.org/bot%s/sendMessage" % general_bot_token,
                     params={'chat_id': '-1001342160485', 'text': message})
    return redirect(request.META.get('HTTP_REFERER'))


def return_materials(request):
    if request.POST:
        message = 'Возврат товаров\n'
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            return_mat_count = int(request.POST['return'+str(i)])
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

            message += str(i) + '. ' + material.name + '\n' + 'Количество: ' + str(material.quantity) +  '\nКоличество возвратных товаров: '  + str(return_mat_count) + '\n\n'
        if 'comment' in request.POST:
            message += 'Примечение: ' + request.POST['comment']
        requests.get("https://api.telegram.org/bot%s/sendMessage" % general_bot_token,
                     params={'chat_id': '-1001342160485', 'text': message})
    return redirect(request.META.get('HTTP_REFERER'))

class MaterialsView(generic.TemplateView):
    template_name = 'appbase/material/materials.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'object': Object.objects.get(slug=self.kwargs['slug']),
            'materials': Material.objects.filter(
                invoice__request_mat__contract__contstruct_object__slug=self.kwargs['slug'], is_delivery=True)
        }
        return super().get(request, *args, **kwargs)
