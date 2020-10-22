from .models import ReleasedMaterialItem, ReleasedMaterial, WriteoffInstrument, WriteoffInstrumentItem, \
    TransferMaterial, TransferMaterialItem
from django.shortcuts import render, redirect
from django.views import generic
from construction_objects_app.models import ConstructionObject
from contracts_app.models import Contract, RequestForMaterial, InvoiceForPayment
from .models import Material
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from transliterate import slugify
import datetime

import os
from foldable_base.settings import BASE_DIR
from docxtpl import DocxTemplate

import telebot

GENERAL_BOT_TOKEN = '1270115367:AAGCRLBP1iSZhpTniwVYQ9p9fqLysY668ew'
general_bot = telebot.TeleBot(GENERAL_BOT_TOKEN)
channel_id = '-1001342160485'


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ContractMaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/contracts.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant'  or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        contracts = Contract.objects.filter(construction_object=construction_object, status='1')
        self.extra_context = {
            'construction_object': construction_object,
            'contracts': contracts
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class MaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/materials.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        materials = Material.objects.filter(invoice__request_for_material__contract__slug=self.kwargs['slug'],
                                            is_delivery=True, invoice__is_done=True, instrument_code=None)

        self.extra_context = {
            'construction_object': construction_object,
            'materials': materials,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        materials = request.POST.getlist('materials')
        materials = Material.objects.filter(id__in=materials)
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        context = {
            'materials': materials,
            'construction_object': construction_object,
        }
        return render(request, template_name='store_materials_app/release_materials.html', context=context)


def release_materials(request):
    if request.POST:
        if 'contract' in request.POST:
            contract = Contract.objects.get(id=int(request.POST['contract']))
        else:
            contract = Material.objects.get(id=int(request.POST['material1'])).invoice.request_for_material.contract
        construction_object = ConstructionObject.objects.get(contract=contract)
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        is_instrument = False

        released_material = ReleasedMaterial.objects.create(user=request.user, release_date=datetime.datetime.now(),
                                                            contract=contract)
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            released_materials_count = int(request.POST['release' + str(i)])
            material.release_count = material.release_count + released_materials_count

            material.remainder_count = material.remainder_count - released_materials_count
            print(released_materials_count, material.remainder_count)
            is_instrument = material.is_instrument
            material.save()
            ReleasedMaterialItem.objects.create(released_material=released_material, material=material,
                                                release_count=released_materials_count,
                                                remainder_count=material.remainder_count + released_materials_count)
        unique_code = ''
        for i in construction_object.name.split(' '):
            if slugify(i) != None:
                i = slugify(i)
            unique_code += i[0]
        unique_code = unique_code.upper()
        unique_code += '-'

        if is_instrument:
            unique_code += 'I' + str(released_material.id)
        else:
            unique_code += 'M' + str(released_material.id)
        released_material.unique_code = unique_code
        released_material.save()

        indexs = list(range(1, ReleasedMaterialItem.objects.filter(released_material=released_material).count() + 1))
        context = {
            'object_name': ConstructionObject.objects.get(contract=contract).name,
            'object_address': ConstructionObject.objects.get(contract=contract).address,
            'number_contract': contract.number_contract,
            'date_contract': contract.date_contract,
            'date_doc': datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            'number_doc': released_material.unique_code,
            'role': request.user.get_role_display(),
            'name': request.user.first_name + ' ' + request.user.last_name,
            'contract_contractor': contract.contractor,
            'materials': ReleasedMaterialItem.objects.filter(released_material=released_material),
            'indexs': indexs,
            'contract_name': contract.name,
        }

        tpl = DocxTemplate(os.path.join(BASE_DIR, 'mediafiles/nakladnaya.docx'))
        tpl.render(context)
        tpl.save('mediafiles/waybill/nakladnaya-' + contract.name + str(released_material.id) + '.docx')

    return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ReleasedMaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/released_materials_list.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'construction_object': construction_object,
            'released_materials': ReleasedMaterial.objects.filter(contract__slug=self.kwargs['slug'],
                                                                  items__material__instrument_code=None).order_by(
                '-id').distinct(),

        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ReturnReleaseMaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/return_release_mat.html'

    def get(self, request, *args, **kwargs):
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        construction_object = released_material.contract.construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'released_material': released_material,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        contract = Contract.objects.get(realeas_material__id=int(self.kwargs['id']))
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        released_material.is_done = True
        released_material.save()
        print(request.POST)
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            released_material_item = ReleasedMaterialItem.objects.get(material=material,
                                                                      released_material=released_material)
            return_material_count = int(request.POST['return_mat' + str(i)])
            material.release_count = material.release_count - return_material_count
            material.remainder_count = material.remainder_count + return_material_count
            material.save()
            released_material_item.return_count = return_material_count
            released_material_item.save()

            indexs = list(
                range(1, ReleasedMaterialItem.objects.filter(released_material=released_material).count() + 1))
            context = {
                'object_name': ConstructionObject.objects.get(contract=contract).name,
                'object_address': ConstructionObject.objects.get(contract=contract).address,
                'number_contract': contract.number_contract,
                'date_contract': contract.date_contract,
                'date_doc': datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                'number_doc': released_material.unique_code,
                'role': request.user.get_role_display(),
                'name': request.user.first_name + ' ' + request.user.last_name,
                'contract_contractor': contract.contractor,
                'materials': ReleasedMaterialItem.objects.filter(released_material=released_material),
                'indexs': indexs,
                'contract_name': contract.name,
            }
            tpl = DocxTemplate(os.path.join(BASE_DIR, 'mediafiles/nakladnaya_final.docx'))
            tpl.render(context)
            tpl.save('mediafiles/waybill/nakladnaya_final-' + contract.name + str(released_material.id) + '.docx')
        print(released_material.items.all()[0].material.is_instrument)
        if released_material.items.all()[0].material.is_instrument:
            return redirect('/construction_objects/' + contract.construction_object.slug + '/released_instruments')
        else:
            return redirect('/contract/' + contract.slug + '/released_materials')
        # return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class DetailReleaseMaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/detial_released_mat.html'

    def get(self, request, *args, **kwargs):
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        construction_object = released_material.contract.construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'released_material': released_material,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AddReleaseWaybillView(generic.TemplateView):
    template_name = 'store_materials_app/waybill/add_release_waybill.html'

    def get(self, request, *args, **kwargs):
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        construction_object = released_material.contract.construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'released_material': released_material,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        released_waybill = request.FILES['waybill']
        released_material.release_waybill = released_waybill
        released_material.save()
        if released_material.items.all()[0].material.is_instrument:
            return redirect(
                '/construction_objects/' + released_material.contract.construction_object.slug + '/released_instruments')
        else:
            return redirect('/contract/' + released_material.contract.slug + '/released_materials')


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AddFinalWaybillView(generic.TemplateView):
    template_name = 'store_materials_app/waybill/add_final_waybill.html'

    def get(self, request, *args, **kwargs):
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        construction_object = released_material.contract.construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'released_material': released_material,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        released_material = ReleasedMaterial.objects.get(id=int(self.kwargs['id']))
        final_waybill = request.FILES['waybill']
        released_material.final_waybill = final_waybill
        released_material.save()
        if released_material.items.all()[0].material.is_instrument:
            return redirect(
                '/construction_objects/' + released_material.contract.construction_object.slug + '/released_instruments')
        else:
            return redirect('/contract/' + released_material.contract.slug + '/released_materials')


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class InstrumentMateriralView(generic.TemplateView):
    template_name = 'store_materials_app/instruments/instruments.html'

    def get(self, request, *args, **kwargs):
        contstruction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or contstruction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        materials = Material.objects.filter(is_delivery=True, invoice__is_done=True,
                                            invoice__request_for_material__contract__construction_object=contstruction_object,
                                            is_remainder=False, is_instrument=True)
        print(Material.objects.filter(invoice__request_for_material__contract__construction_object=contstruction_object,
                                      is_remainder=False, is_delivery=True, is_instrument=True, invoice__is_done=True))
        self.extra_context = {
            'construction_object': contstruction_object,
            'materials': materials,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        materials = request.POST.getlist('materials')
        materials = Material.objects.filter(id__in=materials)
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        context = {
            'materials': materials,
            'construction_object': construction_object,
        }
        if request.POST['submit'] == 'delivered':
            return render(request, template_name='store_materials_app/release_materials.html', context=context)
        elif request.POST['submit'] == 'writeoff':
            return render(request, template_name='store_materials_app/instruments/writeoff_instruments.html',
                          context=context)


def writeoff_instruments(request):
    if request.POST:
        contract = Material.objects.get(id=int(request.POST['material1'])).invoice.request_for_material.contract
        construction_object = ConstructionObject.objects.get(contract=contract)
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        writeoff_instrument = WriteoffInstrument.objects.create(user=request.user,
                                                                construction_object=construction_object)

        writeoff_count_all = 0
        writeoff_sum_price_all = 0
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            writeoff_count = int(request.POST['writeoff_count' + str(i)])
            material.quantity = material.quantity - writeoff_count

            writeoff_instrument_item = WriteoffInstrumentItem.objects.create(writeoff_instrument=writeoff_instrument,
                                                                             material=material,
                                                                             writeoff_count=writeoff_count)
            writeoff_instrument_item.life_time = (writeoff_instrument_item.created_at - material.created_at).days
            writeoff_instrument_item.save()
            writeoff_count_all += writeoff_count
            writeoff_sum_price_all += writeoff_count * material.price
            material.save()

        context = {
            # 'object_name': ConstructionObject.objects.get(contract=contract).name,
            # 'object_address': ConstructionObject.objects.get(contract=contract).address,
            # 'number_contract': contract.number_contract,
            # 'date_contract': contract.date_contract,
            'date_doc': datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            # 'number_doc': released_material.unique_code,
            # 'role': request.user.get_role_display(),
            'name': request.user.first_name + ' ' + request.user.last_name,
            # 'contract_contractor': contract.contractor,
            'materials': WriteoffInstrumentItem.objects.filter(writeoff_instrument=writeoff_instrument),
            'writeoff_count_all': writeoff_count_all,
            'writeoff_sum_price_all': writeoff_sum_price_all,
            # 'contract_name': contract.name,
        }

        tpl = DocxTemplate(os.path.join(BASE_DIR, 'mediafiles/act_writeoff_instruments.docx'))
        tpl.render(context)
        tpl.save('mediafiles/acts_writeoff/act_writeoff_instruments-' + str(writeoff_instrument.id) + '.docx')

    return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class WriteoffInstrumentsList(generic.ListView):
    model = WriteoffInstrument
    template_name = 'store_materials_app/instruments/writeoff_instruments_list.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        context['construction_object'] = construction_object
        return context


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class WriteoffActDocumentUpload(generic.TemplateView):
    template_name = 'store_materials_app/act_document_upload.html'

    def get(self, request, *args, **kwargs):
        writeoff_instrument = WriteoffInstrument.objects.get(id=self.kwargs['pk'])
        contstruction_object = writeoff_instrument.construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or contstruction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': contstruction_object,
            'writeoff_instrument': writeoff_instrument,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        act_document = request.FILES['document']
        writeoff_instrument = WriteoffInstrument.objects.get(id=self.kwargs['pk'])
        writeoff_instrument.act_document = act_document
        writeoff_instrument.save()
        return redirect(
            '/construction_objects/' + writeoff_instrument.construction_object.slug + '/writeoff_instruments_list')


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ReleasedInstruments(generic.TemplateView):
    template_name = 'store_materials_app/instruments/released_instruments.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'construction_object': construction_object,
            'released_materials': ReleasedMaterial.objects.filter(
                contract__construction_object=construction_object).filter(~Q(items__material__instrument_code=None))
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class GeneralBaseView(generic.TemplateView):
    template_name = 'store_materials_app/general_base.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant'  or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        materials = Material.objects.filter(is_delivery=True, invoice__is_done=True,
                                            invoice__request_for_material__contract__construction_object=construction_object)
        self.extra_context = {
            'construction_object': construction_object,
            'materials': materials,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RemainderMaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/remainder_materials.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        materials = Material.objects.filter(is_delivery=True, invoice__is_done=True,
                                            invoice__request_for_material__contract__construction_object=construction_object,
                                            is_remainder=True)
        invoice = InvoiceForPayment.objects.get(name_company=construction_object.name)

        self.extra_context = {
            'construction_object': construction_object,
            'materials': materials,
            'invoice': invoice,

        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        materials = request.POST.getlist('materials')
        materials = Material.objects.filter(id__in=materials)
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        context = {
            'materials': materials,
            'construction_object': construction_object,
            'construction_objects': ConstructionObject.objects.all(),
        }

        if request.POST['submit'] == 'delivered':
            return render(request, template_name='store_materials_app/release_materials.html', context=context)
        elif request.POST['submit'] == 'transfer':
            return render(request, template_name='store_materials_app/transfer_materials.html', context=context)


def transfer_materials(request):
    if request.POST:
        to_construction_object = ConstructionObject.objects.get(id=int(request.POST['to_construction_object']))
        from_construction_object = ConstructionObject.objects.get(id=int(request.POST['from_construction_object']))
        if request.user.role == 'accountant' or request.user.role == 'purchaser':
            return render(request, template_name='404.html')
        # invoice = InvoiceForPayment.objects.get(name_company=construction_object.name)
        transfer_material = TransferMaterial.objects.create(from_construction_object=from_construction_object,
                                                            to_construction_object=to_construction_object,
                                                            user=request.user)
        for i in range(1, int(request.POST['count']) + 1):
            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            transfer_count = request.POST['transfer_count' + str(i)]
            TransferMaterialItem.objects.create(transfer_material=transfer_material, material=material,
                                                transfer_count=transfer_count)

            # material.invoice = invoice
            # material.save()
        message = '🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔🔔\n'
        message += 'Перевод материалов!\n'
        message += str(transfer_material) + '\n'
        message += 'От: ' + from_construction_object.name + '\n'
        message += 'В: ' + to_construction_object.name + '\n'

        general_bot.send_message(channel_id, text=message)

        # indexs = list(range(1, ReleasedMaterialItem.objects.filter(released_material=released_material).count() + 1))
        # context = {
        #     'object_name': ConstructionObject.objects.get(contract=contract).name,
        #     'object_address': ConstructionObject.objects.get(contract=contract).address,
        #     'number_contract': contract.number_contract,
        #     'date_contract': contract.date_contract,
        #     'date_doc': datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
        #     'number_doc': released_material.unique_code,
        #     'role': request.user.get_role_display(),
        #     'name': request.user.first_name + ' ' + request.user.last_name,
        #     'contract_contractor': contract.contractor,
        #     'materials': ReleasedMaterialItem.objects.filter(released_material=released_material),
        #     'indexs': indexs,
        #     'contract_name': contract.name,
        # }
        #
        # tpl = DocxTemplate(os.path.join(BASE_DIR, 'mediafiles/nakladnaya.docx'))
        # tpl.render(context)
        # tpl.save('mediafiles/waybill/nakladnaya-' + contract.name + str(released_material.id) + '.docx')

    return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class RemainderReleasedMaterialsView(generic.TemplateView):
    template_name = 'store_materials_app/remainder_released_materials.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(contract__slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        self.extra_context = {
            'construction_object': construction_object,
            'released_materials': ReleasedMaterial.objects.filter(items__material__is_remainder=True).order_by(
                '-id').distinct(),

        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TransferedMaterialsList(generic.TemplateView):
    template_name = 'store_materials_app/transfered_materials_list.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        transfer_materials = TransferMaterial.objects.filter(to_construction_object=construction_object, is_access=True)
        self.extra_context = {
            'construction_object': construction_object,
            'transfer_materials': transfer_materials,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TransferedMaterialsItem(generic.TemplateView):
    template_name = 'store_materials_app/transfered_materials_item.html'

    def get(self, request, *args, **kwargs):
        transfer_material = TransferMaterial.objects.get(id=int(self.kwargs['pk']))
        construction_object = transfer_material.to_construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or construction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')

        self.extra_context = {
            'construction_object': construction_object,
            'transfer_material': transfer_material,
        }
        return super().get(request, *args, **kwargs)


def transfer_materials_delivered(request):
    if request.POST:
        transfer_material = TransferMaterial.objects.get(id=int(request.POST['transfer_material']))
        to_construnction_object = transfer_material.to_construction_object
        if request.user.role == 'accountant' or request.user.role == 'purchaser' or to_construnction_object not in list(
                request.user.construction_objects.all()):
            return render(request, template_name='404.html')
        invoice = InvoiceForPayment.objects.get(name_company=to_construnction_object.name)
        for material in transfer_material.transfer_material_item.all():
            if material.transfer_count == material.material.remainder_count:
                material.material.invoice = invoice
                material.material.save()
            else:
                material.material.remainder_count = material.material.remainder_count - material.transfer_count
                material.material.save()
                Material.objects.create(invoice=invoice, quantity=material.transfer_count, ok=material.transfer_count,
                                        remainder_count=material.transfer_count, is_delivery=True, status='ок',
                                        is_remainder=True, name=material.material.name, units=material.material.units,
                                        price=material.material.price, is_instrument=material.material.is_instrument)
        transfer_material.is_delivered = True
        transfer_material.save()
        return redirect('/transfered_material/' + str(transfer_material.id) + '/detail')
