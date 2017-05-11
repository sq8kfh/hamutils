import datetime
from hamutils.cabrillo import CabrilloWriter


f=open('./test.cbr', 'wb')
cbr = CabrilloWriter(f)
cbr.write_tag('CALLSIGN', 'SQ8TEST')
cbr.write_tags(category='SINGLE-OP ALL LOW', contest='SOME-CONTEST')
cbr.add_qso('15m', 'PH', datetime.datetime.utcnow(), 'SQ8TEST', '59', '001LN', 'K0TEST', '59', '003LN')
cbr.add_qso('15m', 'PH', datetime.datetime.utcnow(), 'SQ8TEST', '59', '002LN', 'SP0TEST', '59', '123LN')
cbr.close()
