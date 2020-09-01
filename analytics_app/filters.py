import django_filters
from material_app.models import Material


class MaterialFilter(django_filters.FilterSet):
    class Meta:
        model = Material
        fields = ['price', 'units'  ]

