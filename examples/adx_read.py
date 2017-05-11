from hamutils.adif import ADXReader


f=open('./test.adx', 'r')
adx = ADXReader(f)
for qso in adx:
    print(qso)
