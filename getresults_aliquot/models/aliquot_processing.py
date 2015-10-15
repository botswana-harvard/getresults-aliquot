from django.db import models

from edc_base.model.models import BaseUuidModel
from edc_base.audit_trail import AuditTrail


class AliquotProcessing(BaseUuidModel):

    print_labels = models.BooleanField(
        verbose_name='Print aliquot labels now',
        default=True,
        help_text='If checked, labels will be printed immediately.')

    history = AuditTrail()

    def __str__(self):
        return self.aliquot.aliquot_identifier

#     def save(self, *args, **kwargs):
#         lab_profile = site_lab_profiles.registry.get(
#             self.aliquot.receive.requisition_model_name)
#         lab_profile().aliquot_by_profile(
#             self.aliquot,
#             self.profile)
#         super(AliquotProcessing, self).save(*args, **kwargs)

    class Meta:
        app_label = 'getresults_aliquot'
        db_table = 'getresults_aliquotprocessing'
