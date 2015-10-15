from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .aliquot import Aliquot, AliquotType
from django.core.exceptions import MultipleObjectsReturned


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


@receiver(post_save, weak=False, dispatch_uid='create_aliquot_on_post_save')
def create_aliquot_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Creates and aliquot after a sample is received."""
    if not raw:
        if created:
            try:
                aliquot_type = AliquotType.objects.get(alpha_code=instance.specimen_type.alpha_code)
                try:
                    Aliquot.objects.get(receive=instance)
                except Aliquot.DoesNotExist:
                    Aliquot.objects.create(
                        receive=instance,
                        aliquot_type=aliquot_type)
                except MultipleObjectsReturned:
                    pass
            except AttributeError:
                pass
