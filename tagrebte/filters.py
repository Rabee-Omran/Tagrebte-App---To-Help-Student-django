import django_filters
from .models import PostType

class TypeFilter(django_filters.FilterSet):

    #filter contains
    types = django_filters.CharFilter( label ="ابحث عن فرعك ", lookup_expr='icontains')
    class Meta:
        model = PostType
        fields = ('types',)
       