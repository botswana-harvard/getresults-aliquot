import factory

from getresults_aliquot.models import Aliquot


class AliquotFactory(factory.DjangoModelFactory):

    class Meta:
        model = Aliquot
