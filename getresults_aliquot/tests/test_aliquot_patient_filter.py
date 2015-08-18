from ..admin import AliquotAdmin
from ..filters import AliquotPatientFilter
from ..models import Aliquot

from .base_aliquot_test import BaseTestAliquot


class TestAliquotPatientFilter(BaseTestAliquot):

    def test_aliquot_patient_filter(self):
        """Test if the queryset will filter by patient protocol."""
        Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier='AA3456700000201',
            aliquot_type=self.aliquot_type,
        )
        patient_filter = AliquotPatientFilter(
            None,
            {'receive__patient__protocol': self.receive.patient.protocol},
            Aliquot, AliquotAdmin
        )
        aliquot = patient_filter.queryset(None, Aliquot.objects.all())[0]
        self.assertEqual(aliquot.receive.patient.protocol, self.patient.protocol)
