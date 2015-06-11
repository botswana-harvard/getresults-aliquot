from django.db import models

from edc_base.model.models import BaseUuidModel


class AliquotCondition(BaseUuidModel):

    name = models.CharField(
        max_length=10,
        unique=True)

    description = models.CharField(
        max_length=25,
        unique=True)

    display_order = models.IntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return '{} {}'.format(self.short_name.upper(), self.name)

    class Meta:
        app_label = 'aliquot'
        ordering = ("name", )
