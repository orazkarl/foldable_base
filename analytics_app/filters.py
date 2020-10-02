import django_filters
from contracts_app.models import Contract
from django import forms


class MaterialFilter(django_filters.FilterSet):
    contract = django_filters.ChoiceFilter('invoice__request_for_material__contract__name', choices=[], label='Работа',
                                           lookup_expr='iexact', widget=forms.Select(
            attrs={'class': 'form-control', 'placeholder': 'Работа'}))
    contract_status = django_filters.ChoiceFilter('invoice__request_for_material__contract__status', label='Статус работы',
                                                  choices=Contract.STATUS_WORK,
                                                  widget=forms.Select(
                                                      attrs={'class': 'form-control', 'placeholder': 'Статус работы'}))
    request_done = django_filters.BooleanFilter('invoice__request_for_material__is_done', label='Заявка обработана?',
                                                widget=forms.NullBooleanSelect(attrs={'class': 'form-control',
                                                                                      'placeholder':
                                                                                          'Заявка обработана?'}))
    units = django_filters.ChoiceFilter('units', label='ед. изм.', choices=[],
                                        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'ед. изм.'}))
    instrument = django_filters.BooleanFilter('is_instrument', label='Инструмент?', widget=forms.NullBooleanSelect(
        attrs={'class': 'form-control', 'placeholder': 'Инструмент?'}))

    is_cash = django_filters.BooleanFilter('invoice__is_cash', label='Наличный?', widget=forms.NullBooleanSelect(
        attrs={'class': 'form-control', 'placeholder': 'Наличный?'}))

    def __init__(self, *args, **kwargs):
        super(MaterialFilter, self).__init__(*args, **kwargs)
        construction_object = self.queryset[0].invoice.request_for_material.contract.construction_object
        contract_choices = self.filters['contract'].extra['choices']
        contract_choices += [
            (subcat.name, subcat.name) for subcat
            in Contract.objects.filter(construction_object=construction_object)
        ]
        units_choices = self.filters['units'].extra['choices']
        units_choices += [
            (subcat, subcat) for subcat
            in self.queryset.values_list('units', flat=True).distinct()
        ]

    start_date = django_filters.DateFilter('created_at', lookup_expr='gte', widget=forms.DateInput(
        attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}), label='Дата от')
    end_date = django_filters.DateFilter('created_at', lookup_expr='lte', widget=forms.DateInput(
        attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}), label='Дата до')


class ReleasedMaterialFilter(django_filters.FilterSet):
    contract = django_filters.ChoiceFilter('contract__name', choices=[], label='Работа',
                                           lookup_expr='iexact', widget=forms.Select(
            attrs={'class': 'form-control', 'placeholder': 'Работа'}))

    start_date = django_filters.DateFilter('release_date', lookup_expr='gte', widget=forms.DateInput(
        attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}), label='Дата от')
    end_date = django_filters.DateFilter('release_date', lookup_expr='lte', widget=forms.DateInput(
        attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}), label='Дата до')

    def __init__(self, *args, **kwargs):
        super(ReleasedMaterialFilter, self).__init__(*args, **kwargs)
        construction_object = self.queryset[0].contract.construction_object
        contract_choices = self.filters['contract'].extra['choices']
        contract_choices += [
            (subcat.name, subcat.name) for subcat
            in Contract.objects.filter(construction_object=construction_object)
        ]
