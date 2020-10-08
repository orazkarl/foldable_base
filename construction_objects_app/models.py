from django.db import models
# from contracts_app.models import Contract, RequestForMaterial, InvoiceForPayment

slug_help_text = "Слаг - это короткая метка для представления страницы в URL. \
Содержит только буквы, цифры, подчеркивания или дефисы."


class ConstructionObject(models.Model):
    name = models.CharField('Название', max_length=250, unique=True)
    slug = models.SlugField(max_length=250, null=True, blank=True, help_text=slug_help_text, db_index=True, unique=True)
    address = models.CharField('Адрес', max_length=250)
    image = models.ImageField('Изображение', upload_to='images', null=True, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)

    def save(self, *args, **kwargs):
        # self.contract_set.create
        contract = self.contract_set.create(construction_object=self, name=self.name)
        request_for_material = contract.request_for_material.create(contract=contract, name=self.name, is_done=True)
        invoice = request_for_material.invoice_for_payment.create(request_for_material=request_for_material, name_company=self.name, is_paid=True, is_done=True, is_looked=True, status='да')
        return super(ConstructionObject, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Обьекты'




