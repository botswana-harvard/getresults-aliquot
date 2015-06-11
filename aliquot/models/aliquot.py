import datetime

from django.db import models

from getresults.models import Receive

from edc_base.model.models import BaseUuidModel

from ..choices import ALIQUOT_STATUS, SPECIMEN_MEASURE_UNITS, SPECIMEN_MEDIUM
from ..managers import AliquotManager

from .aliquot_condition import AliquotCondition
from .aliquot_type import AliquotType


class Aliquot (BaseUuidModel):

    primary_aliquot = models.ForeignKey(
        'self',
        null=True,
        related_name='primary',
        editable=False)

    source_aliquot = models.ForeignKey(
        'self',
        null=True,
        related_name='source',
        editable=False,
        help_text=('Aliquot from which this aliquot was created,'
                   'Leave blank if this is the primary tube')
    )

    aliquot_identifier = models.CharField(
        verbose_name='Aliquot Identifier',
        max_length=25,
        unique=True,
        help_text="Aliquot identifier",
        editable=False)

    aliquot_datetime = models.DateTimeField(
        verbose_name="Date and time aliquot created",
        default=datetime.datetime.today())

    receive = models.ForeignKey(Receive)

    aliquot_type = models.ForeignKey(AliquotType, verbose_name="Aliquot Type")

    aliquot_condition = models.ForeignKey(
        AliquotCondition,
        verbose_name="Aliquot Condition",
        default=10,
        null=True)

    parent_identifier = models.ForeignKey(
        'self',
        to_field='aliquot_identifier',
        blank=True,
        null=True)

    count = models.IntegerField(
        editable=False,
        null=True)

    medium = models.CharField(
        verbose_name='Medium',
        max_length=25,
        choices=SPECIMEN_MEDIUM,
        default='TUBE')

    original_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='5.00')

    current_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='5.00')

    measure_units = models.CharField(
        max_length=25,
        choices=SPECIMEN_MEASURE_UNITS,
        default='mL')

    status = models.CharField(
        max_length=25,
        choices=ALIQUOT_STATUS,
        default='available')

    comment = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    subject_identifier = models.CharField(
        max_length=50,
        null=True,
        editable=False,
        help_text="non-user helper field to simplify search and filtering")

    is_packed = models.BooleanField(
        verbose_name='packed',
        default=False)

    receive_identifier = models.CharField(
        max_length=25,
        null=True,
        editable=False,
        help_text="non-user helper field to simplify search and filter")

    objects = AliquotManager()

    def __str__(self):
        return self.aliquot_identifier

    def save(self, *args, **kwargs):
        self.subject_identifier = self.receive.patient.subject_identifier
        self.receive_identifier = self.receive.receive_identifier
        super(Aliquot, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.aliquot_identifier,)

    def barcode_value(self):
        return self.aliquot_identifier

    class Meta:
        app_label = 'aliquot'
