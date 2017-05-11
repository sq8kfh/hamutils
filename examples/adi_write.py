import datetime
from hamutils.adif import ADIWriter


f=open('./test.adi', 'wb')
adi = ADIWriter(f)
adi.add_qso(call='K0TEST', datetime_on=datetime.datetime.utcnow(), band='15m', mode='USB', name='some not ascii characters: ąęśżźćółń', app_hamutils_somefield='some data')
adi.add_qso(call='SP0TEST', datetime_on=datetime.datetime.utcnow(), band='10m', mode='USB', name='some not ascii characters: 北京')
adi.close()
