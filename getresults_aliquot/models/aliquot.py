import re

from django.conf import settings
from django.db import models
from django.utils import timezone

from getresults_receive.models import Receive
from simple_history.models import HistoricalRecords as AuditTrail
from edc_base.model.models import BaseUuidModel

from ..exceptions import AliquotError
from ..managers import AliquotManager

from .aliquot_condition import AliquotCondition
from .aliquot_type import AliquotType

ALIQUOT_STATUS = (
    ('available', 'available'),
    ('consumed', 'consumed'),
)

SPECIMEN_MEASURE_UNITS = (
    ('mL', 'mL'),
    ('uL', 'uL'),
    ('spots', 'spots'),
    ('n/a', 'Not Applicable'),
)

SPECIMEN_MEDIUM = (
    ('tube_any', 'Tube'),
    ('tube_edta', 'Tube EDTA'),
    ('swab', 'Swab'),
    ('dbs_card', 'DBS Card'),
)


class BaseAliquot (BaseUuidModel):

    verify_identifier_pattern = True

    @property
    def prefix_pattern(self):
        checkdigit_pattern = ''  # [0-9]{1}'
        try:
            prefix = settings.ALIQUOT_IDENTIFIER_PREFIX_PATTERN
        except AttributeError:
            prefix = '\w+'
        return prefix + checkdigit_pattern

    receive = models.ForeignKey(Receive, null=True)

    receive_identifier = models.CharField(max_length=25, null=True, blank=False)

    aliquot_datetime = models.DateTimeField(
        verbose_name="Date and time getresults_aliquot created",
        default=timezone.now)

    aliquot_type = models.ForeignKey(AliquotType)

    aliquot_condition = models.ForeignKey(
        to=AliquotCondition,
        null=True,
        blank=False)

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
        editable=False)

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

    history = AuditTrail()

    objects = AliquotManager()

    def __str__(self):
        return self.aliquot_identifier

    def get_aliquot_identifier(self, prefix):
        """Returns an aliquot identifier create from a source aliquot or,
        if PRIMARY, from the receive identifier."""
        parent_segment = self.get_parent_segment(self.parent_aliquot_identifier)
        count_segment = str(self.count).zfill(2)
        stub = '{0}{1}{2}'.format(
            parent_segment, self.aliquot_type.numeric_code.zfill(2), count_segment)
        try:
            return '{0}{1}'.format(prefix, stub)
        except AttributeError:
            return '{0}{1}'.format(prefix, stub)

    def save(self, *args, **kwargs):
        self.receive = self.receive or Receive.objects.get(receive_identifier=self.receive_identifier)
        self.receive_identifier = self.receive_identifier or self.receive.receive_identifier
        self.count = self.get_count(self.parent_aliquot_identifier, count=self.count)
        if not self.aliquot_identifier:
            self.aliquot_identifier = self.get_aliquot_identifier(prefix=self.receive_identifier)
        if self.get_parent_segment(self.aliquot_identifier) == '0000':
            self.parent_aliquot_identifier = None
            self.primary_aliquot_identifier = self.aliquot_identifier
        else:
            if not self.parent_aliquot_identifier or not self.primary_aliquot_identifier:
                raise AliquotError(
                    'Aliquot is not the primary aliquot. Please specify the primary and parent aliquot. '
                    'Got primary=\'{}\', parent=\'{}\''.format(
                        self.primary_aliquot_identifier, self.parent_aliquot_identifier))
        if self.verify_identifier_pattern:
            self.validate_identifier_pattern(self.aliquot_identifier)
            self.validate_identifier_pattern(self.parent_aliquot_identifier)
            self.validate_identifier_pattern(self.primary_aliquot_identifier)
        super(BaseAliquot, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.aliquot_identifier, )

    def parent_aliquot(self):
        """Returns the parent aliquot instance."""
        try:
            return self.__class__.get(aliquot_identifier=self.parent_aliquot_identifier)
        except self.__class__.DoesNotExist:
            return None

    def barcode_value(self):
        return self.aliquot_identifier

    def validate_identifier_pattern(self, identifier):
        if identifier:
            if not re.match(self.identifier_pattern, identifier):
                raise AliquotError(
                    'Invalid aliquot identifier format. Got {}'.format(identifier))

    @property
    def identifier_pattern(self):
        return re.compile(
            '^{}(0000|[0-9]{{3}}[1-9]{{1}})([0-9]{{3}}[1-9]{{1}})$'.format(
                self.prefix_pattern))

    def get_identifier_prefix(self, value=None):
        value = value or self.aliquot_identifier
        match = re.search(self.prefix_pattern, value)
        return match.group()

    def get_own_segment(self, value=None):
        value = value or self.aliquot_identifier
        return value[-4:]

    def get_parent_segment(self, value=None):
        value = value or self.aliquot_identifier
        if not value:
            return '0000'
        return value[-8:-4]

    def get_count(self, value=None, count=None):
        value = value or self.aliquot_identifier
        if count:
            return count
        elif not value:
            return 1
        return int(value[-2:])

    @property
    def number(self):
        """Aliquot number relative to primary."""
        return int(self.aliquot_identifier[-2:])

    @property
    def is_primary(self):
        """Primary aliquot is always aliquot 1."""
        return self.aliquot_identifier[-1:] == '1'

    class Meta:
        abstract = True


class Aliquot(BaseAliquot):

    class Meta:
        app_label = 'getresults_aliquot'
        db_table = 'getresults_aliquot'
