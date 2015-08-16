from django.contrib import admin

from getresults.admin import admin_site

from ..models import AliquotProcessing


class AliquotProcessingAdmin(admin.ModelAdmin):

    list_display = ('getresults_aliquot', 'profile', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = (
        'aliquot__aliquot_identifier',
        'profile__profile_name',
        'aliquot__aliquot_type__name',
        'aliquot__aliquot_type__alpha_code',
        'aliquot__aliquot_type__numeric_code')

    list_filter = ('processing_profile', 'created', 'modified', 'user_created', 'user_modified')

admin_site.register(AliquotProcessing, AliquotProcessingAdmin)
