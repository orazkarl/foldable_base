from django.shortcuts import HttpResponse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from construction_objects_app.models import ConstructionObject, Contract, RequestForMaterial
from material_app.models import Material, ReleasedMaterial
from .filters import MaterialFilter, ReleasedMaterialFilter
from django.db.models import Sum
import datetime
import pytz
import csv


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AnalyticsView(generic.ListView):
    template_name = 'analytics/analytics.html'
    model = Material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset().filter(is_delivery=True, invoice__is_done=True,
                                              invoice__request_for_material__contract__construction_object__slug=
                                              self.kwargs['slug'])
        material_filter = MaterialFilter(self.request.GET, queryset=queryset)
        context['total_sum_price'] = material_filter.qs.aggregate(Sum('sum_price'))['sum_price__sum']
        context['filter'] = material_filter

        return context

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        self.extra_context = {
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TotalStats(generic.TemplateView):
    template_name = 'analytics/total_stats.html'

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        contracts = Contract.objects.filter(construction_object=construction_object)
        request_mats = RequestForMaterial.objects.filter(contract__construction_object=construction_object)
        materials = Material.objects.filter(
            invoice__request_for_material__contract__construction_object=construction_object)
        total_sum_price = materials.aggregate(Sum('sum_price'))['sum_price__sum']

        start_date_default = datetime.datetime(2020, 8, 1, tzinfo=pytz.UTC)
        end_date_default = datetime.datetime.today().date()
        in_work = contracts.filter(status='1')
        finished = contracts.filter(status='2')
        not_finished = contracts.filter(status='3')
        check = contracts.filter(status='4')
        is_done_request_mat = request_mats.filter(is_done=True)
        if 'start_date' in request.GET:
            start_date_default = request.GET['start_date'].replace('-', '/')
            end_date_default = request.GET['end_date'].replace('-', '/')
            start_date_default = datetime.datetime.strptime(start_date_default, '%Y/%m/%d')
            end_date_default = datetime.datetime.strptime(end_date_default, '%Y/%m/%d')
            contracts = contracts.filter(created_at__gte=start_date_default,
                                         created_at__lte=end_date_default)
            request_mats = request_mats.filter(created_at__gte=start_date_default,
                                               created_at__lte=end_date_default)
            materials = materials.filter(created_at__gte=start_date_default,
                                         created_at__lte=end_date_default + datetime.timedelta(days=1))

            in_work = contracts.filter(status='1')
            finished = contracts.filter(status='2')
            not_finished = contracts.filter(status='3')
            check = contracts.filter(status='4')
            is_done_request_mat = request_mats.filter(is_done=True)
            total_sum_price = materials.aggregate(Sum('sum_price'))['sum_price__sum']

        self.extra_context = {
            'construction_object': construction_object,
            'contracts': contracts,
            'request_mats': request_mats,
            'materials': materials,
            'total_sum_price': total_sum_price,
            'start_date_default': start_date_default,
            'end_date_default': end_date_default,
            'in_work': in_work,
            'finished': finished,
            'not_finished': not_finished,
            'check': check,
            'is_done_request_mat': is_done_request_mat,

        }
        return super().get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ReleasedMaterialsStats(generic.ListView):
    template_name = 'analytics/release_mat_stats.html'
    model = ReleasedMaterial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        queryset = queryset.filter(contract__construction_object=construction_object).order_by('-release_date')
        self.queryset = queryset
        release_material_filter = ReleasedMaterialFilter(self.request.GET, queryset=queryset)
        context['filter'] = release_material_filter

        return context

    def get(self, request, *args, **kwargs):
        construction_object = ConstructionObject.objects.get(slug=self.kwargs['slug'])
        self.extra_context = {
            'construction_object': construction_object,
        }
        return super().get(request, *args, **kwargs)


def export_analytics(request, slug):
    if request.POST:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        writer.writerow(
            ['#', 'Название', 'Работа', 'Статус работы', 'Заявка обработана?', 'Количество',
             'Отпущено', 'Остаток', 'ед. изм.', 'Код инструмента', 'Наличный?', 'Цена', 'Сумма'])
        count_materiras = int(request.POST['count_materials'])

        for i in range(1, count_materiras + 1):
            request_for_material_done = 'Нет'
            invoice_is_cash = 'Нет'

            material = Material.objects.get(id=int(request.POST['material' + str(i)]))
            if material.invoice.request_for_material.is_done:
                request_for_material_done = 'Да'
            if material.invoice.is_cash:
                invoice_is_cash = 'Да'
            if material.instrument_code is None:
                material.instrument_code = 'Нет'
            writer.writerow([str(i), material.name, material.invoice.request_for_material.contract.name,
                             material.invoice.request_for_material.contract.get_status_display(),
                             request_for_material_done, material.quantity, material.release_count,
                             material.quantity - material.release_count, material.units, material.instrument_code,
                             invoice_is_cash, material.price, material.sum_price])
        writer.writerow(
            ['Итого: ' + str(count_materiras), '', '', '', '', '', '', '', '', '', '', '',
             request.POST['total_sum_price']])

        return response
