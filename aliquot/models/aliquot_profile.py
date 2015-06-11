from django.db import models

from edc_base.model.models import BaseUuidModel


class AliquotProfile(BaseUuidModel):

    name = models.CharField(
        verbose_name='Profile Name',
        max_length=50,
        unique=True)

    objects = models.Manager()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'aliquot'
        ordering = ("name", )
