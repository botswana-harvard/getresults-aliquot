from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords


class AliquotCondition(BaseUuidModel):

    name = models.CharField(
        max_length=10,
        unique=True)

    description = models.CharField(
        max_length=25,
        unique=True)

    display_order = models.IntegerField(default=0)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.name.upper(), self.description)

    class Meta:
        app_label = 'getresults_aliquot'
        db_table = 'getresults_aliquotcondition'
        ordering = ("name", )
