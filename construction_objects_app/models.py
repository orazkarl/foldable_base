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



    # def save(self, *args, **kwargs):

        # contract = self.contract.create(construction_object=self, name=self.name)
        # contract.save()
        # request_for_material = contract.request_for_material.create(contract=contract, name=self.name, is_done=True)
        # invoice = request_for_material.invoice_for_payment.create(request_for_material=request_for_material, name_company=self.name, is_paid=True, is_done=True, is_looked=True, status='да')
        # super(ConstructionObject, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Обьекты'
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=ConstructionObject, dispatch_uid="update_stock_count")
def update_stock(sender, instance, **kwargs):
    print(list(instance.contract.filter(name=instance.name) )== [])
    if list(instance.contract.filter(name=instance.name) )== []:
        contract = instance.contract.create(construction_object=instance, name=instance.name)
        request_for_material = contract.request_for_material.create(contract=contract, name=instance.name, is_done=True)
        invoice = request_for_material.invoice_for_payment.create(request_for_material=request_for_material, name_company=instance.name, is_paid=True, is_done=True, is_looked=True, status='да')