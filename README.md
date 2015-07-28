[![Build Status](https://travis-ci.org/botswana-harvard/getresults-aliquot.svg)](https://travis-ci.org/botswana-harvard/getresults-aliquot)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-aliquot/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/getresults-aliquot?branch=develop)
# getresults-aliquot

Identifier Scheme

The aliquot identifier has three segments:
- unique prefix: based on the receiving identifier. this is a string that is unique across all aliquots in the system. 
- parent segment: 4 digits. Digits 1,2 are the parent sample type, digits 3,4 are the parent aliquot number. 
- own segment: 4 digits. Digits 1,2 are the sample type, digits 3,4 are the aliquot number.

For example, a whole blood primary tube is received as 'AA99999'. The code for whole blood is '02'.
	
	from getresults_aliquot.models import Aliquot, AliquotType
	AliquotType.objects.create(
	    name='whole blood',
	    alpha_code='WB',
	    numeric_code='02')
	
	primary_aliquot = Aliquot.objects.create_primary(prefix='AA99999', numeric_code='02')
	print(primary_aliquot.aliquot_identiier)
	'AA9999900000201'
	
Create three aliquots from the primary  