from django.db import models
from appbase.models import InvoiceForPayment, Contract
from django.conf import settings


class Material(models.Model):
    MATERIAL_CHOICES = [
        ['-', '-'],
        ['ок', 'ок'],
        ['брак', 'брак'],
        # ['нехватка', 'нехватка'],
        # ['несоответствие', 'несоответствие'],
    ]

    # request_mat = models.ForeignKey(RequestForMaterial, on_delete=models.CASCADE, verbose_name='Заявка',
    #                                 related_name='material')
    invoice = models.ForeignKey(InvoiceForPayment, on_delete=models.CASCADE, verbose_name='Счет на оплату',
                                related_name='material')
    name = models.CharField('Название', max_length=250)
    quantity = models.PositiveIntegerField('Количество', default=0)
    ok = models.PositiveIntegerField('Ок', default=0)
    brak = models.PositiveIntegerField('Брак', default=0)
    nexvatka = models.PositiveIntegerField('Нехватка', default=0)
    nesotvetsvie = models.PositiveIntegerField('Несоответсвие', default=0)
    units = models.CharField('Единицы измерения', max_length=20, null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=15, decimal_places=2)
    sum_price = models.DecimalField('Сумма', max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField('Статус', max_length=250, choices=MATERIAL_CHOICES, default='-')
    is_delivery = models.BooleanField('Доставлен?', default=False)
    instrument_code = models.CharField('Код инструмента', max_length=250, null=True, blank=True)
    is_instrument = models.BooleanField('Инструмен?', default=False)
    created_at = models.DateTimeField( auto_now_add=True)
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


class ReleaseMaterial(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    release_date = models.DateTimeField('Когда отпустил?', auto_now_add=True)
    # return_date = models.DateTimeField('Когда принял обратно?', null=True, blank=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='realeas_material',
                                 verbose_name='Работа')
    release_waybill = models.FileField(upload_to='waybill/', null=True, blank=True)
    final_waybill = models.FileField(upload_to='waybill/', null=True, blank=True)
    is_done = models.BooleanField('Обработан?', default=False)

    class Meta:
        verbose_name = 'Отпускаемые материалы'
        verbose_name_plural = 'Отпускаемые материалы'

    def __str__(self):
        return (str(self.id))


class ReleaseMaterialItem(models.Model):
    release_material = models.ForeignKey(ReleaseMaterial, related_name='items', on_delete=models.CASCADE,
                                         verbose_name='Отпускаемый материал')
    material = models.ForeignKey(Material, related_name='realease_material_items', on_delete=models.CASCADE,
                                 verbose_name='Материал')
    release_count = models.PositiveIntegerField('Сколько отпустил?')
    return_count = models.PositiveIntegerField('Возвращено', default=0)

    def __str__(self):
        return self.material.name
