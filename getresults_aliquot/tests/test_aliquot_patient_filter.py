from django.test import TestCase
from django.utils import timezone

from getresults_aliquot.models import Aliquot, AliquotType
from getresults_receive.models import Receive, Patient
from ..admin import AliquotAdmin
from ..filters import AliquotPatientFilter


class TestAliquotPaitentFilter(TestCase):

    @property
    def patient(self):
        return Patient.objects.create(
            patient_identifier='P12345678',
            protocol='protocol_1',
            registration_datetime=timezone.now())

    @property
    def receive(self):
        return Receive.objects.create(
            receive_identifier='AA34567',
            patient=self.patient,
            receive_datetime=timezone.now())

    @property
    def aliquot_type(self):
        return AliquotType.objects.create(
            name='whole blood', alpha_code='WB', numeric_code='02')

    def test_aliquot_patient_filter(self):
        """Test if the quesry set will filter by patient protocol."""
        Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier='AA3456700000201',
            aliquot_type=self.aliquot_type,
        )
        filter = AliquotPatientFilter(None, {'receive__patient__protocol': self.patient.protocol}, Aliquot, AliquotAdmin)
        aliquot = filter.queryset(None, Aliquot.objects.all())[0]
        self.assertEqual(aliquot.patient.protocol, self.patient.protocol)
