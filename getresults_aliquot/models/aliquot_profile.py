from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords


class AliquotProfile(BaseUuidModel):

    name = models.CharField(
        verbose_name='Profile Name',
        max_length=50,
        unique=True)

    history = HistoricalRecords()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'getresults_aliquot'
        db_table = 'getresults_aliquotprofile'
        ordering = ("name", )