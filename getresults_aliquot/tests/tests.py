import re
from copy import copy

from django.test import TestCase
from django.utils import timezone

from getresults_aliquot.exceptions import AliquotError
from getresults_aliquot.models import Aliquot, AliquotType
from getresults_receive.models import Receive
from getresults_patient.models import Patient
from getresults.tests.base_selenium_test import BaseSeleniumTest


good_pattern = '[A-Z]{2}[0-9]{5}'
Aliquot.prefix_pattern = good_pattern


class TestSelenium(BaseSeleniumTest):

    def test_admin(self):
        self.navigate_to_admin()
        self.login()


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

    def test_good_pattern(self):
        good_pattern = '[A-Z]{2}[0-9]{5}'
        Aliquot.prefix_pattern = good_pattern
        aliquot_identifier = 'AA3456700000201'
        self.assertEqual(aliquot_identifier.split('00000201')[0], re.match(good_pattern, aliquot_identifier).group())
        receive = self.receive
        aliquot_type = self.aliquot_type
        self.assertIsInstance(
            Aliquot.objects.create(
                receive=receive,
                aliquot_identifier=aliquot_identifier,
                aliquot_type=aliquot_type,
            ),
            Aliquot
        )
        self.assertEqual(
            aliquot_identifier,
            Aliquot.objects.get(aliquot_identifier=aliquot_identifier).aliquot_identifier)

    def test_bad_pattern(self):
        bad_pattern = '[A-Z]{3}[0-9]{5}'
        Aliquot.prefix_pattern = bad_pattern
        aliquot_identifier = 'AA3456700000201'
        self.assertIsNone(re.match(bad_pattern, aliquot_identifier))
        receive = self.receive
        aliquot_type = self.aliquot_type
        self.assertRaises(
            AliquotError,
            Aliquot.objects.create,
            receive=receive,
            aliquot_identifier=aliquot_identifier,
            aliquot_type=aliquot_type,
        )
        Aliquot.prefix_pattern = good_pattern

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
        receive = self.receive
        aliquot_type = self.aliquot_type
        primary = Aliquot.objects.create_primary(receive, aliquot_type.numeric_code)
        self.assertTrue(primary.is_primary)
        self.assertEqual(primary.aliquot_identifier, 'AA3456700000201')

    def test_is_not_primary(self):
        receive = self.receive
        aliquot_type = self.aliquot_type
        primary = Aliquot.objects.create_primary(receive, aliquot_type.numeric_code)
        aliquot = Aliquot(
            receive=receive,
            aliquot_identifier='AA3456702010202',
            parent_aliquot_identifier='AA3456700000201',
            primary_aliquot_identifier=primary.aliquot_identifier,
            aliquot_type=aliquot_type,
        )
        alq = copy(aliquot)
        primary = Aliquot.objects.create_primary(alq.receive, '02')
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

    def test_create_aliquot_from_primary(self):
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
