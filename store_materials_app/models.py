from django.db import models
from django.conf import settings
from contracts_app.models import InvoiceForPayment, Contract
from paid_material_app.models import Material


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


class WriteoffInstrument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField('Когда списал?', auto_now_add=True)

    class Meta:
        verbose_name = 'Акт списания инструмента'
        verbose_name_plural = 'Акт списания инструментов'

    def __str__(self):
        return f"Списанные инструменты: {self.id}"


class WriteoffInstrumentItem(models.Model):
    writeoff_instrument = models.ForeignKey(WriteoffInstrument, related_name='writeoff_instrument_item', on_delete=models.CASCADE,
                                 verbose_name='Акт списания инструмента')
    material = models.ForeignKey(Material, related_name='writeoff_instrument_item', on_delete=models.CASCADE,
                                 verbose_name='Материал')
    writeoff_count = models.PositiveIntegerField('Сколько списано?')

    def __str__(self):
        return self.material.name
