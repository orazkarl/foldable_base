from django.db import models
from django.contrib.auth.models import AbstractUser
from construction_objects_app.models import ConstructionObject


class User(AbstractUser):
    USER_ROLES = [
        ['admin', 'админ'],  # админ
        ['purchaser', 'закупщик'],  # закупщик
        ['accountant', 'бухгалтер'],  # бухгалтер
        ['manager', 'завсклад']  # завсклад

    ]

    city = models.CharField('Город', max_length=100, null=True)
    address = models.CharField('Адрес', max_length=250, null=True)
    role = models.CharField('Должность', max_length=50, choices=USER_ROLES)
    construction_objects = models.ManyToManyField(ConstructionObject, related_name='contstruct_objects', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=12, null=True, blank=True)
    id_passport = models.CharField('ИИН', max_length=12, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
