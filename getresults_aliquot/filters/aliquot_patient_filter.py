from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class AliquotPatientFilter(SimpleListFilter):

    title = _('patient')
    parameter_name = 'patient_protocol'

    def lookups(self, request, model_admin):
        patients = model_admin.model.objects.all()
        return [(patient.protocol) for patient in patients]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(receive__patient__protocol=self.value())
        else:
            return queryset
