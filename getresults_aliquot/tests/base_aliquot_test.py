from django.test import TransactionTestCase
from django.utils import timezone

from getresults_aliquot.models import Aliquot, AliquotType
from getresults_receive.models import Receive
from getresults_patient.models import Patient


good_pattern = '[A-Z]{2}[0-9]{5}'

Aliquot.prefix_pattern = good_pattern


class BaseTestAliquot(TransactionTestCase):

    def setUp(self):
        patient_identifier = 'P12345678'

        self.patient = Patient.objects.create(
            patient_identifier=patient_identifier,
            registration_datetime=timezone.now())

        self.receive = Receive.objects.create(
            receive_identifier='AA34567',
            patient=self.patient,
            receive_datetime=timezone.now(),
            collection_datetime=timezone.now(),
            specimen_condition='10',
            tube_count=1)

        self.aliquot_type = AliquotType.objects.create(
            name='whole blood', alpha_code='WB', numeric_code='02')
