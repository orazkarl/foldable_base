from django.db import models

slug_help_text = "Слаг - это короткая метка для представления страницы в URL. \
Содержит только буквы, цифры, подчеркивания или дефисы."


class Object(models.Model):
    name = models.CharField('Название', max_length=250)
    slug = models.SlugField(max_length=250, null=True, blank=True, help_text=slug_help_text, db_index=True, unique=True)
    address = models.CharField('Адрес', max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Обьекты'


class Contract(models.Model):
    STATUS_WORK = [
        ['выполнено', 'выполнено'],
        ['невыполнено', 'невыполнено'],
        ['проверка', 'проверка'],
        ['выполнение', 'выполнение']
    ]

    contstruct_object = models.ForeignKey(Object, on_delete=models.CASCADE, verbose_name='Строительный объект')
    name = models.CharField('Название', max_length=250)
    slug = models.SlugField(max_length=250, null=True, blank=True, help_text=slug_help_text, db_index=True, unique=True)
    contractor = models.CharField('Подрядчик', max_length=250, null=True, blank=True)
    contract = models.FileField('Договор', upload_to='contracts/')
    number_contract = models.CharField('Номер договора', max_length=250)
    status = models.CharField('Статус работы', max_length=100, choices=STATUS_WORK)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Подярд'
        verbose_name_plural = 'Подярды'


class Material(models.Model):
    MATERIAL_CHOICES = [
        ['ок', 'ок'],
        ['брак', 'брак'],
        ['нехватка', 'нехватка'],
        ['несоответствие', 'несоответствие'],
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Подряд')
    name = models.CharField('Название', max_length=250)
    quantity = models.PositiveIntegerField('Количество', default=0)
    units = models.CharField('Единицы измерения', max_length=20, null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=15, decimal_places=2)
    sum_price = models.DecimalField('Сумма', max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField('Статус', max_length=250, choices=MATERIAL_CHOICES, default='ок')

    def save(self, *args, **kwargs):
        self.sum_price = self.quantity * self.price
        return super(Material, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class RequestForMaterial(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Подряд', related_name='request')
    name = models.CharField('Название', max_length=100)
    file = models.FileField('Документ (заявка)', upload_to='request/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class InvoiceForPayment(models.Model):
    STATUS_CHOICES = [
        ['да', 'да'],
        ['нет', 'нет'],
        ['потом', 'потом']
    ]
    # contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Подряд', related_name='invoice')
    request_mat = models.ForeignKey(RequestForMaterial, on_delete=models.CASCADE, verbose_name='Заявка', related_name='invoice')
    file = models.FileField('Документ (счет на оплату)', upload_to='invoices/')
    status = models.CharField('Статус ответа', choices=STATUS_CHOICES, max_length=10, default='нет')

    class Meta:
        verbose_name = 'Счет на оплату'
        verbose_name_plural = 'Счета на оплату'
