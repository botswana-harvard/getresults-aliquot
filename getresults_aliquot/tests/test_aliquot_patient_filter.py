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

    def test_create_get(self):
        aliquot_identifier = 'AA3456700000201'
        Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier=aliquot_identifier,
            aliquot_type=self.aliquot_type,
        )
        self.assertEqual(
            aliquot_identifier,
            Aliquot.objects.get(aliquot_identifier=aliquot_identifier).aliquot_identifier)

        filter = admin.AliquotPatientFilter(None, {'patient': self.patient}, Aliquot, admin.AliquotAdmin)
        aliquot = filter.queryset(None, Aliquot.objects.all())[0]
        self.assertEqual(aliquot.patient, self.patient)
