from django.db import models
from construction_objects_app.models import ConstructionObject
from transliterate import slugify



slug_help_text = "Слаг - это короткая метка для представления страницы в URL. \
Содержит только буквы, цифры, подчеркивания или дефисы."

class Contract(models.Model):
    STATUS_WORK = [
        ['1', 'в работе'],
        ['2', 'выполнено'],
        ['3', 'проверка'],
        ['4', 'невыполнено'],
    ]

    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE,
                                            verbose_name='Строительный объект')
    name = models.CharField('Название работы', max_length=250, unique=True)
    slug = models.SlugField(max_length=250, null=True, blank=True, help_text=slug_help_text, db_index=True, unique=True)
    contractor = models.CharField('Подрядчик', max_length=250, null=True, blank=True)
    contract_file = models.FileField('Договор', upload_to='contracts/')
    bin = models.CharField('БИН', max_length=100)
    date_contract = models.DateField('Дата договора', null=True, blank=True)
    number_contract = models.CharField('Номер договора', max_length=250)
    status = models.CharField('Статус работы', max_length=100, choices=STATUS_WORK)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Работы'
        verbose_name_plural = 'Работы'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Contract, self).save(*args, **kwargs)


class RequestForMaterial(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Работа',
                                 related_name='request_for_material')
    name = models.CharField('Название', max_length=100)
    doc_file = models.FileField('Документ (заявка)', upload_to='request_for_materiral/')
    is_done = models.BooleanField('Отработан?', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class InvoiceForPayment(models.Model):
    STATUS_CHOICES = [
        ['-', '-'],
        ['да', 'да'],
        ['нет', 'нет'],
        ['потом', 'потом']
    ]
    request_for_material = models.ForeignKey(RequestForMaterial, on_delete=models.CASCADE, verbose_name='Заявка',
                                             related_name='invoice_for_payment')
    bin = models.CharField('БИН', max_length=100)
    name_company = models.CharField('Название компании', max_length=250)
    comment = models.CharField('Примечение', max_length=1000, null=True, blank=True)
    doc_file = models.FileField('Документ (счет на оплату)', upload_to='invoices/')
    status = models.CharField('Статус ответа', choices=STATUS_CHOICES, max_length=10, default='-')
    is_paid = models.BooleanField('Оплачен?', default=False)
    is_looked = models.BooleanField('Просмотрен?', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменен', auto_now=True)
    reset_date = models.DateTimeField('Дата сброса', null=True, blank=True)
    is_done = models.BooleanField('Отработан?', default=False)
    is_cash = models.BooleanField('Наличный?', default=False)

    class Meta:
        verbose_name = 'Счет на оплату'
        verbose_name_plural = 'Счета на оплату'

    def __str__(self):
        return self.name_company
