from django.db.models.signals import pre_save
from django.dispatch import receiver

from .aliquot import Aliquot


@receiver(pre_save, weak=False, dispatch_uid='aliquot_check_primary_exists')
def aliquot_check_primary_exists(sender, instance, raw, using, **kwargs):
    if not raw:
        try:
            if not instance.is_primary:
                try:
                    Aliquot.objects.get(aliquot_identifier=instance.primary_aliquot_identifier)
                except Aliquot.DoesNotExist:
                    raise Aliquot.DoesNotExist(
                        'Primary aliquot {} does not exist'.format(
                            instance.primary_aliquot_identifier)
                    )
        except AttributeError:
            pass
