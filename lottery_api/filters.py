from django_filters import rest_framework as filters

from lottery_api.models import (
    LotoSeven,
    LotoSix,
    MiniLoto
)


class LotoSevenFilter(filters.FilterSet):
    times = filters.RangeFilter(field_name='times')
    lottery_date = filters.DateFromToRangeFilter(field_name='lottery_date')
    number_1 = filters.CharFilter(field_name='number_1', lookup_expr='exact')
    number_2 = filters.CharFilter(field_name='number_2', lookup_expr='exact')
    number_3 = filters.CharFilter(field_name='number_3', lookup_expr='exact')
    number_4 = filters.CharFilter(field_name='number_4', lookup_expr='exact')
    number_5 = filters.CharFilter(field_name='number_5', lookup_expr='exact')
    number_6 = filters.CharFilter(field_name='number_6', lookup_expr='exact')
    number_7 = filters.CharFilter(field_name='number_7', lookup_expr='exact')
    bonus_number1 = filters.CharFilter(field_name='bonus_number1', lookup_expr='exact')
    bonus_number2 = filters.CharFilter(field_name='bonus_number2', lookup_expr='exact')
    lottery_number = filters.CharFilter(field_name='lottery_number', lookup_expr='contains')

    class Meta:
        model = LotoSeven
        fields = ['times']


class LotoSixFilter(filters.FilterSet):
    times = filters.RangeFilter(field_name='times')
    lottery_date = filters.DateFromToRangeFilter(field_name='lottery_date')
    number_1 = filters.CharFilter(field_name='number_1', lookup_expr='exact')
    number_2 = filters.CharFilter(field_name='number_2', lookup_expr='exact')
    number_3 = filters.CharFilter(field_name='number_3', lookup_expr='exact')
    number_4 = filters.CharFilter(field_name='number_4', lookup_expr='exact')
    number_5 = filters.CharFilter(field_name='number_5', lookup_expr='exact')
    number_6 = filters.CharFilter(field_name='number_6', lookup_expr='exact')
    bonus_number1 = filters.CharFilter(field_name='bonus_number1', lookup_expr='exact')
    bonus_number2 = filters.CharFilter(field_name='bonus_number2', lookup_expr='exact')
    lottery_number = filters.CharFilter(field_name='lottery_number', lookup_expr='contains')

    class Meta:
        model = LotoSix
        fields = ['times']


class MiniLotoFilter(filters.FilterSet):
    times = filters.RangeFilter(field_name='times')
    lottery_date = filters.DateFromToRangeFilter(field_name='lottery_date')
    number_1 = filters.CharFilter(field_name='number_1', lookup_expr='exact')
    number_2 = filters.CharFilter(field_name='number_2', lookup_expr='exact')
    number_3 = filters.CharFilter(field_name='number_3', lookup_expr='exact')
    number_4 = filters.CharFilter(field_name='number_4', lookup_expr='exact')
    number_5 = filters.CharFilter(field_name='number_5', lookup_expr='exact')
    bonus_number1 = filters.CharFilter(field_name='bonus_number1', lookup_expr='exact')
    lottery_number = filters.CharFilter(field_name='lottery_number', lookup_expr='contains')

    class Meta:
        model = MiniLoto
        fields = ['times']
