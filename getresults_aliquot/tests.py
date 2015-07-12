from copy import copy

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from getresults_aliquot.exceptions import AliquotError
from getresults_aliquot.models import Aliquot, AliquotType
from getresults_receive.models import Receive, Patient


class TestAliquot(TestCase):

    @property
    def patient(self):
        patient_identifier = 'P12345678'
        return Patient.objects.create(
            patient_identifier=patient_identifier,
            registration_datetime=timezone.now())

    @property
    def receive(self):
        return Receive.objects.create(
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

    def test_is_primary(self):
        aliquot = Aliquot(
            receive=self.receive,
            aliquot_identifier='AA3456700000201',
            aliquot_type=self.aliquot_type,
        )
        aliquot.save()
        self.assertTrue(aliquot.is_primary)
        self.assertIsNone(aliquot.parent_aliquot_identifier)
        self.assertEqual(aliquot.primary_aliquot_identifier, aliquot.aliquot_identifier)

    def test_create_primary(self):
        aliquot = Aliquot(
            receive=self.receive,
            aliquot_identifier='AA3456700000201',
            primary_aliquot_identifier='AA3456700000201',
            aliquot_type=self.aliquot_type,
        )
        primary = Aliquot.objects.create_primary(aliquot)
        self.assertTrue(primary.is_primary)
        self.assertEqual(primary.aliquot_identifier, 'AA3456700000201')

    def test_create_bad_primary(self):
        aliquot = Aliquot(
            receive=self.receive,
            aliquot_identifier='AA3456700000202',
            primary_aliquot_identifier='AA3456700000202',
            aliquot_type=self.aliquot_type,
        )
        self.assertRaises(Aliquot.DoesNotExist, Aliquot.objects.create_primary, aliquot)

    def test_is_not_primary(self):
        aliquot = Aliquot(
            receive=self.receive,
            aliquot_identifier='AA3456702010202',
            parent_aliquot_identifier='AA3456700000201',
            primary_aliquot_identifier='AA3456700000201',
            aliquot_type=self.aliquot_type,
        )
        primary = Aliquot.objects.create_primary(copy(aliquot))
        self.assertTrue(primary.is_primary)
        self.assertEqual(primary.aliquot_identifier, 'AA3456700000201')
        aliquot.save()
        self.assertFalse(aliquot.is_primary)
        self.assertIsNotNone(aliquot.parent_aliquot_identifier, 'parent_aliquot_identifier')
        self.assertNotEqual('', aliquot.parent_aliquot_identifier)
        self.assertIsNotNone(aliquot.primary_aliquot_identifier)
        self.assertNotEqual('', aliquot.primary_aliquot_identifier, 'primary_aliquot_identifier')
        self.assertNotEqual(aliquot.primary_aliquot_identifier, aliquot.aliquot_identifier)
        self.assertNotEqual(aliquot.parent_aliquot_identifier, aliquot.aliquot_identifier)

    def test_identifier_format(self):
        # can't end in 8 zeros
        aliquot_identifier = '123456700000000'
        aliquot = Aliquot(
            receive=self.receive,
            aliquot_identifier=aliquot_identifier,
            aliquot_type=self.aliquot_type,
        )
        self.assertRaises(AliquotError, aliquot.save)
        # too short
        aliquot.aliquot_identifier = 'AA34567'
        self.assertRaises(AliquotError, aliquot.save)
        # must end in 8 numerics
        aliquot.aliquot_identifier = 'AA34567AAAA0000'
        self.assertRaises(AliquotError, aliquot.save)
        # own segment cannot be 4 zeros
        aliquot.aliquot_identifier = 'AA3456700010000'
        self.assertRaises(AliquotError, aliquot.save)
        # 1st aliquot from primary aliquot
        aliquot.aliquot_identifier = 'AA3456700000201'
        aliquot.parent_aliquot_identifier = 'AA3456700000201'
        aliquot.save()
        aliquot.aliquot_identifier = 'AA3456700010002'
        aliquot.parent_aliquot_identifier = 'AA3456700010001'
        aliquot.save()

    def test_create_aliquot_from_primay(self):
        aliquot_identifier = 'AA3456700000201'
        aliquot = Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier=aliquot_identifier,
            aliquot_type=self.aliquot_type,
        )
        aliquots = Aliquot.objects.create_aliquots(aliquot)
        self.assertEqual(aliquots[0].aliquot_identifier, 'AA3456702010202')

    def test_create_aliquot_from_child(self):
        aliquot_identifier = 'AA3456700000201'
        aliquot = Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier=aliquot_identifier,
            aliquot_type=self.aliquot_type,
        )
        aliquots = Aliquot.objects.create_aliquots(aliquot)
        aliquots = Aliquot.objects.create_aliquots(aliquots[0], count=3)
        self.assertEqual(aliquots[0].aliquot_identifier, 'AA3456702020203')
        self.assertEqual(aliquots[1].aliquot_identifier, 'AA3456702020204')
        self.assertEqual(aliquots[2].aliquot_identifier, 'AA3456702020205')

    def test_create_plasma_aliquot_from_whole_blood_child(self):
        AliquotType.objects.create(name='plasma', alpha_code='PL', numeric_code='32')
        aliquot_identifier = 'AA3456700000201'
        aliquot = Aliquot.objects.create(
            receive=self.receive,
            aliquot_identifier=aliquot_identifier,
            aliquot_type=self.aliquot_type,
        )
        aliquots = Aliquot.objects.create_aliquots(aliquot)
        aliquots = Aliquot.objects.create_aliquots(aliquots[0], numeric_code='32', count=3)
        self.assertEqual(aliquots[0].aliquot_identifier, 'AA3456702023203')
        self.assertEqual(aliquots[1].aliquot_identifier, 'AA3456702023204')
        self.assertEqual(aliquots[2].aliquot_identifier, 'AA3456702023205')
