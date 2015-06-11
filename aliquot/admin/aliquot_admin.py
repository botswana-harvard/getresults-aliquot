from django.contrib import admin

from ..models import Aliquot, AliquotCondition, AliquotType


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
    readonly_fields = ('aliquot_identifier',)
admin.site.register(Aliquot, AliquotAdmin)


class AliquotTypeAdmin(admin.ModelAdmin):
    list_display = ('alpha_code', 'numeric_code', 'name', 'description', 'created', 'modified')
admin.site.register(AliquotType, AliquotTypeAdmin)


class AliquotConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created', 'modified')
admin.site.register(AliquotCondition, AliquotConditionAdmin)
