from hamutils.qrz import Qrz
import getpass


user = input("qrz's login: ")
password = getpass.getpass("qrz's password: ")

qrz = Qrz()

res = qrz.lookup('SQ8KFH', username=user, password=password)
print(res)
