import re

from django.conf import settings
from django.db import models
from django.utils import timezone

from getresults_receive.models import Receive

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from ..choices import ALIQUOT_STATUS, SPECIMEN_MEASURE_UNITS, SPECIMEN_MEDIUM
from ..exceptions import AliquotError
from ..managers import AliquotManager

from .aliquot_condition import AliquotCondition
from .aliquot_type import AliquotType


class Aliquot (BaseUuidModel):

    identifier_pattern = re.compile(
        '^{}(0000|[0-9]{{3}}[1-9]{{1}})([0-9]{{3}}[1-9]{{1}})$'.format(
            settings.ALIQUOT_IDENTIFIER_PREFIX_PATTERN))

    receive = models.ForeignKey(Receive)

    aliquot_datetime = models.DateTimeField(
        verbose_name="Date and time getresults_aliquot created",
        default=timezone.now)

    aliquot_type = models.ForeignKey(AliquotType)

    aliquot_condition = models.ForeignKey(
        AliquotCondition,
        null=True)

    aliquot_identifier = models.CharField(
        verbose_name='Aliquot Identifier',
        max_length=16,
        unique=True,
        help_text="Aliquot identifier",
        editable=False)

    primary_aliquot_identifier = models.CharField(
        max_length=16,
        editable=False,
        help_text=('Primary aliquot from which this aliquot originates')
    )

    parent_aliquot_identifier = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        help_text=('Immediate aliquot from which this aliquot was created,'
                   'Leave blank if this is the primary tube')
    )

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

    is_packed = models.BooleanField(
        verbose_name='packed',
        default=False)

    verify_identifier_pattern = models.BooleanField(
        default=True)

    history = HistoricalRecords()

    objects = AliquotManager()

    def __str__(self):
        return self.aliquot_identifier

    def save(self, *args, **kwargs):
        if self.parent_segment == '0000':
            self.parent_aliquot_identifier = None
            self.primary_aliquot_identifier = self.aliquot_identifier
        else:
            if not self.parent_aliquot_identifier:
                raise AliquotError(
                    'Expected parent aliquot. Got None')
            if not self.primary_aliquot_identifier:
                raise AliquotError(
                    'Expected primary aliquot. Got None')
        if self.verify_identifier_pattern:
            self.check_identifier_pattern(self.aliquot_identifier)
            self.check_identifier_pattern(self.parent_aliquot_identifier)
            self.check_identifier_pattern(self.primary_aliquot_identifier)
        super(Aliquot, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.aliquot_identifier,)

    def parent_aliquot(self):
        """Returns the parent aliquot instance."""
        try:
            return self.__class__.get(aliquot_identifier=self.parent_aliquot_identifier)
        except self.__class__.DoesNotExist:
            return None  # will be None if this is the primary

    def barcode_value(self):
        return self.aliquot_identifier

    def check_identifier_pattern(self, identifier):
        if identifier:
            if not re.match(self.identifier_pattern, identifier):
                raise AliquotError(
                    'Invalid aliquot identifier format. Got {}'.format(identifier))

    @property
    def identifier_prefix(self):
        match = re.search(settings.ALIQUOT_IDENTIFIER_PREFIX_PATTERN, self.aliquot_identifier)
        return match.group()

    @property
    def own_segment(self):
        return self.aliquot_identifier[-4:]

    @property
    def parent_segment(self):
        return self.aliquot_identifier[-8:11]

    @property
    def number(self):
        """Aliquot number relative to primary."""
        return int(self.aliquot_identifier[-2:])

    @property
    def is_primary(self):
        """Primary aliquot is always aliquot 1."""
        return self.aliquot_identifier[-1:] == '1'

    class Meta:
        app_label = 'getresults_aliquot'
        db_table = 'getresults_aliquot'
