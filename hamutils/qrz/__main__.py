import getpass
import argparse

from . import Qrz


def main():
    parser = argparse.ArgumentParser(description='Call lookup on qrz.com')
    parser.add_argument('calls', metavar='call', nargs='+', help='callsign')
    parser.add_argument('-u', '--username', help="qrz.com's username")

    args = parser.parse_args()

    user = args.username
    if not user:
        user = input("qrz's login: ")
    password = getpass.getpass("qrz's password: ")

    qrz = Qrz()

    for call in args.calls:
        res = qrz.lookup(call, username=user, password=password)
        print(res)
    print(qrz.message)


if __name__ == "__main__":
    main()
