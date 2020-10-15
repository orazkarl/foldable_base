from django.db import models
from django.conf import settings
from contracts_app.models import InvoiceForPayment, Contract
from paid_material_app.models import Material
from construction_objects_app.models import ConstructionObject


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
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE,
                                            related_name='writeoff_instrument',
                                            verbose_name='Объект')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField('Когда списал?', auto_now_add=True)
    act_document = models.FileField('Документ', upload_to='acts_writeoff/', null=True, blank=True)

    class Meta:
        verbose_name = 'Акт списания инструмента'
        verbose_name_plural = 'Акт списания инструментов'

    def __str__(self):
        return f"Списанные инструменты: {self.id}"


class WriteoffInstrumentItem(models.Model):
    writeoff_instrument = models.ForeignKey(WriteoffInstrument, related_name='writeoff_instrument_item',
                                            on_delete=models.CASCADE,
                                            verbose_name='Акт списания инструмента')
    material = models.ForeignKey(Material, related_name='writeoff_instrument_item', on_delete=models.CASCADE,
                                 verbose_name='Материал')
    writeoff_count = models.PositiveIntegerField('Сколько списано?')
    writeoff_sum_price = models.PositiveIntegerField('Сумма')
    life_time = models.PositiveIntegerField('Срок службы', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.material.name

    def save(self, *args, **kwargs):
        self.writeoff_sum_price = self.writeoff_count * self.material.price
        return super(WriteoffInstrumentItem, self).save(*args, **kwargs)


class TransferMaterial(models.Model):
    from_construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, verbose_name='Объект', related_name='from_transfer_material')
    to_construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, verbose_name='Объект', related_name='to_transfer_material')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True)
    is_access = models.BooleanField('Доступ', default=False)
    is_delivered = models.BooleanField('Доставлено', default=False)
    # act_document = models.FileField('Документ', upload_to='acts_writeoff/', null=True, blank=True)

    class Meta:
        verbose_name = 'Перевод материала'
        verbose_name_plural = 'Перевод материалов'

    def __str__(self):
        return f"Перевод материалов: {self.id}"

class TransferMaterialItem(models.Model):
    transfer_material = models.ForeignKey(TransferMaterial, related_name='transfer_material_item',
                                            on_delete=models.CASCADE,
                                            verbose_name='Перевод материалов')
    material = models.ForeignKey(Material, related_name='transfer_material_item_material', on_delete=models.CASCADE,verbose_name='Материал')
    transfer_count = models.PositiveIntegerField('Количество')
    # writeoff_sum_price = models.PositiveIntegerField('Сумма')
    # life_time = models.PositiveIntegerField('Срок службы', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.material.name