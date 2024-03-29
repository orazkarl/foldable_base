from django import forms
from contracts_app.models import Contract, RequestForMaterial, InvoiceForPayment


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['name', 'contractor', 'contract_file', 'bin', 'date_contract', 'number_contract', 'status']
        widgets = {
            'date_contract': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


class RequestForMaterialForm(forms.ModelForm):
    class Meta:
        model = RequestForMaterial
        fields = ['doc_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


class InvoiceForPaymentForm(forms.ModelForm):
    class Meta:
        model = InvoiceForPayment
        fields = ['bin', 'name_company', 'doc_file', 'is_cash', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'type': 'textarea'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name != 'is_cash':
                visible.field.widget.attrs['class'] = 'form-control'
                visible.field.widget.attrs['autocomplete'] = 'off'
