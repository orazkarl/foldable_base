from django.db import models
from contracts_app.models import InvoiceForPayment, Contract



class Material(models.Model):
    MATERIAL_CHOICES = [
        ['-', '-'],
        ['ок', 'ок'],
        ['брак', 'брак'],
    ]

    invoice = models.ForeignKey(InvoiceForPayment, on_delete=models.CASCADE, verbose_name='Счет на оплату',
                                related_name='material', null=True, blank=True)
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
    is_remainder = models.BooleanField('Это остаток?', default=False)

    def save(self, *args, **kwargs):
        self.sum_price = self.quantity * self.price
        return super(Material, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


