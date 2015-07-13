from django.apps import apps
from django.db import models, IntegrityError


class AliquotManager(models.Manager):

    def get_by_natural_key(self, aliquot_identifier):
        return self.get(aliquot_identifier=aliquot_identifier)

    def create_aliquots(self, aliquot, numeric_code=None, measure=None, count=None):
        """Creates and returns a list of aliquots instances."""
        created = []
        AliquotType = apps.get_model(self.model._meta.app_label, 'aliquottype')
        count = count or 1
        aliquot_type = aliquot.aliquot_type
        numeric_code = numeric_code or aliquot.aliquot_type.numeric_code
        numeric_code = str(numeric_code)
        measure = measure or aliquot.original_measure
        if numeric_code != aliquot.aliquot_type.numeric_code:
            aliquot_type = AliquotType.objects.get(numeric_code=numeric_code)
        for index in range(1, count + 1):
            aliquot_identifier = '{0}{1}{2}{3:02d}'.format(
                aliquot.identifier_prefix,
                aliquot.own_segment,
                numeric_code, aliquot.number + index)
            new_aliquot = self.create(
                receive=aliquot.receive,
                aliquot_identifier=aliquot_identifier,
                parent_aliquot_identifier=aliquot.aliquot_identifier,
                primary_aliquot_identifier=aliquot.primary_aliquot_identifier,
                aliquot_type=aliquot_type)
            created.append(new_aliquot)
        return created

    def create_primary(self, aliquot):
        """Creates and returns an primary aliquot (get or create)."""
        try:
            primary_aliquot = self.get(aliquot_identifier=aliquot.primary_aliquot_identifier)
        except self.model.DoesNotExist:
            primary_aliquot = self.create(
                receive=aliquot.receive,
                aliquot_identifier=aliquot.primary_aliquot_identifier,
                parent_aliquot_identifier=None,
                primary_aliquot_identifier=aliquot.primary_aliquot_identifier,
                aliquot_type=aliquot.aliquot_type)
        return primary_aliquot
