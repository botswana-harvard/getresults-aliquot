from django.contrib import admin

from getresults.admin import admin_site

from ..models import AliquotProfile, AliquotProfileItem


class AliquotProfileItemInlineAdmin(admin.TabularInline):
    model = AliquotProfileItem


class AliquotProfileAdmin(admin.ModelAdmin):

    list_display = ('name', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('name', 'aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = (
        'aliquot_type__name',
        'aliquot_type__alpha_code',
        'aliquot_type__numeric_code',
        'created',
        'modified',
        'user_created',
        'user_modified')

    inlines = [AliquotProfileItemInlineAdmin]

admin_site.register(AliquotProfile, AliquotProfileAdmin)
