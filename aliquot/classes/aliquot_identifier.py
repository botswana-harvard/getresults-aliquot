

class AliquotIdentifier(object):

    def format(self, **kwargs):
        receive = kwargs.get('receive')
        aliquot_type = kwargs.get('aliquot_type')
        parent_aliquot = kwargs.get('parent_aliquot')
        if parent_aliquot:
            parent_segment = str(parent_aliquot.aliquot_type.numeric_code).rjust(2, '0') + str(parent_aliquot.count).rjust(2, '0')
            self_count = parent_aliquot.count + 1
        else:
            parent_segment = ''.rjust(4, '0')
            self_count = 1
        # todo: might be a good place to do a sanity check on 'parent' to 'self' aliquot type
        self_segment = aliquot_type.numeric_code.rjust(2, '0') + str(self_count).rjust(2, '0')
        return '%s%s%s' % (receive.receive_identifier, parent_segment, self_segment)

    @property
    def identifier(self, **kwargs):
        receive = kwargs.get('receive')
        if not receive:
            raise TypeError('AliquotManager.create_aliquot needs a receiving record. Got none.')
        aliquot_type = kwargs.get('aliquot_type')
        if not aliquot_type:
            raise TypeError('AliquotManager.create_aliquot needs an aliquot_type. Got none.')
        qset = Q()
        parent_identifier = kwargs.get('parent_identifier')
        if parent_identifier:
            qset.add(Q(aliquot_identifier=parent_identifier), Q.AND)
            parent_aliquot = super(AliquotManager, self).filter(qset).order_by('-count')[0]
        else:
            parent_aliquot = super(AliquotManager, self).none()
        if parent_identifier and not parent_aliquot:
            # you specified a parent but it does not exist, abandon...
            aliquot_identifier = ''
        else:
            # create a new primary aliquot OR a child aliquot
            if parent_aliquot:
                # create a child
                aliquot_identifier = self._format_identifier(
                    receive=receive,
                    parent_aliquot=parent_aliquot,
                    aliquot_type=aliquot_type)
            else:
                # create a new aliquot (primary)
                aliquot_identifier = self._format_identifier(
                    receive=receive,
                    aliquot_type=aliquot_type)

        return aliquot_identifier
    