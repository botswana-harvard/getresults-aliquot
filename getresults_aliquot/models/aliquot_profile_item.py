from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords


class AliquotProfileItem(BaseUuidModel):

    volume = models.DecimalField(
        verbose_name='Volume (ml)',
        max_digits=10,
        decimal_places=1,
        null=True)

    count = models.IntegerField(
        verbose_name='aliquots to create')

    history = HistoricalRecords()

    class Meta:
        app_label = 'getresults_aliquot'
        db_table = 'getresults_aliquotprofileitem'
