from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class AliquotPatientFilter(SimpleListFilter):

    title = _('patient_protocol')
    parameter_name = 'patient_protocol'

    def lookups(self, request, model_admin):
        return (('protocol_1', 'protocol_1'), ('protocol_2', 'protocol_2'), )

    def queryset(self, request, queryset):
        if self.value() == 'protocol_1':
            return queryset.filter(receive__patient__protocol='')
        if self.value() == 'protocol_2':
            return queryset.filter(receive__patient__protocol='')
