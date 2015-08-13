from django.contrib import admin
from django.test import TestCase
from django.utils import timezone

from getresults_aliquot.models import Aliquot, AliquotType
from getresults_receive.models import Receive, Patient
from getresults_aliquot.admin import AliquotAdmin
from getresults_aliquot.filters import AliquotPatientFilter


class TestAliquotPaitentFilter(TestCase):

    @property
    def patient(self):
        patient_identifier = 'P12345678'
        return Patient.objects.create(
            patient_identifier=patient_identifier,
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

    @property
    def aliquot(self):
        """Test if the quesry set will filter by patient protocol."""
        Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier='AA3456700000201',
            aliquot_type=self.aliquot_type,
        )
        filter = admin.AliquotPatientFilter(None, {'receive__patient__protocol': self.patient.protocol}, Aliquot, admin.AliquotAdmin)
        aliquot = filter.queryset(None, Aliquot.objects.all())[0]
        self.assertEqual(aliquot.patient.protocol, self.patient.protocol)
