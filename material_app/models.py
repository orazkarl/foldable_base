from django.db import models
from construction_objects_app.models import InvoiceForPayment, Contract
from django.conf import settings
import uuid


class Material(models.Model):
    MATERIAL_CHOICES = [
        ['-', '-'],
        ['ок', 'ок'],
        ['брак', 'брак'],
    ]

    invoice = models.ForeignKey(InvoiceForPayment, on_delete=models.CASCADE, verbose_name='Счет на оплату',
                                related_name='material')
    name = models.CharField('Название', max_length=250)
    quantity = models.PositiveIntegerField('Количество', default=0)
    ok = models.PositiveIntegerField('Ок', default=0)
    marriage = models.PositiveIntegerField('Брак', default=0)
    shortage = models.PositiveIntegerField('Нехватка', default=0)
    inconsistency = models.PositiveIntegerField('Несоответствие', default=0)
    units = models.CharField('Единицы измерения', max_length=20, null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=15, decimal_places=2)
    sum_price = models.DecimalField('Сумма', max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField('Статус', max_length=250, choices=MATERIAL_CHOICES, default='-')
    is_delivery = models.BooleanField('Доставлен?', default=False)
    instrument_code = models.CharField('Код инструмента', max_length=250, null=True, blank=True)
    is_instrument = models.BooleanField('Инструмент?', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)
    release_count = models.PositiveIntegerField('Ушли', default=0)
    remainder_count = models.PositiveIntegerField('Остаток', default=0)

    def save(self, *args, **kwargs):
        self.sum_price = self.quantity * self.price
        return super(Material, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class ReleasedMaterial(models.Model):
    unique_code = models.CharField(unique=True, max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    release_date = models.DateTimeField('Когда отпустил?', auto_now_add=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='realeas_material',
                                 verbose_name='Работа')
    release_waybill = models.FileField(upload_to='waybill/', null=True, blank=True)
    final_waybill = models.FileField(upload_to='waybill/', null=True, blank=True)
    is_done = models.BooleanField('Обработан?', default=False)

    class Meta:
        verbose_name = 'Отпускаемые материалы'
        verbose_name_plural = 'Отпускаемые материалы'

    def __str__(self):
        return f"Отпущенные материалы: {self.unique_code}"


class ReleasedMaterialItem(models.Model):
    released_material = models.ForeignKey(ReleasedMaterial, related_name='items', on_delete=models.CASCADE,
                                         verbose_name='Отпускаемый материал')
    material = models.ForeignKey(Material, related_name='release_material_items', on_delete=models.CASCADE,
                                 verbose_name='Материал')
    remainder_count = models.PositiveIntegerField('Сколько было?')
    release_count = models.PositiveIntegerField('Сколько отпустил?')
    return_count = models.PositiveIntegerField('Возвращено', default=0)

    def __str__(self):
        return self.material.name
