from hamutils.adif import ADIReader


f=open('./test.adi', 'r', encoding="ascii")
adi = ADIReader(f)
for qso in adi:
    print(qso)
