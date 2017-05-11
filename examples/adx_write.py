import datetime
from hamutils.adif import ADXWriter


f=open('./test.adx', 'wb')
adx = ADXWriter(f)
adx.add_qso(call='K0TEST', datetime_on=datetime.datetime.utcnow(), band='15m', mode='USB', name='some not ascii characters: ąęśżźćółń', app_hamutils_somefield='some data')
adx.add_qso(call='SP0TEST', datetime_on=datetime.datetime.utcnow(), band='10m', mode='USB', name='some not ascii characters: 北京')
adx.close()
