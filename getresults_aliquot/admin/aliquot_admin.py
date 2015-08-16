from django.contrib import admin

from getresults.admin import admin_site

from ..models import Aliquot, AliquotCondition, AliquotType
from ..filters import AliquotPatientFilter


class AliquotAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj:  # In edit mode
            return ('aliquot_type', 'receive', 'original_measure',) + self.readonly_fields
        else:
            return self.readonly_fields
    fields = ('aliquot_identifier', 'receive', 'aliquot_type', 'medium', 'original_measure',
              'current_measure', 'measure_units', 'aliquot_condition', 'status', 'comment')
    list_display = ('aliquot_identifier', 'aliquot_type', 'original_measure', 'current_measure',
                    'measure_units', 'aliquot_condition', 'receive')
    list_filter = (AliquotPatientFilter)
    readonly_fields = ('aliquot_identifier',)
admin_site.register(Aliquot, AliquotAdmin)


class AliquotTypeAdmin(admin.ModelAdmin):
    list_display = ('alpha_code', 'numeric_code', 'name', 'description', 'created', 'modified')
admin_site.register(AliquotType, AliquotTypeAdmin)


class AliquotConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created', 'modified')
admin_site.register(AliquotCondition, AliquotConditionAdmin)
