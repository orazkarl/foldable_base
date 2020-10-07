from django import forms
from .models import Material
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'quantity', 'units', 'price', 'sum_price', 'is_instrument']
        # widgets = {
        #     'comment': forms.Textarea(attrs={'type': 'textarea'})
        # }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.name != 'is_instrument':
                visible.field.widget.attrs['class'] = 'form-control'
                visible.field.widget.attrs['autocomplete'] = 'off'
