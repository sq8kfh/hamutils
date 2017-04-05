from .solar_data import get_solar_data
from .geomagnetic_data import get_geomagnetic_data
from .predictions import get_space_weather_predictions

import argparse


def main():
    parser = argparse.ArgumentParser(description='Get space weather from NOAA/SWPC')
    parser.add_argument('-g', '--geomagnetic', help="get geomagnetic data", action='store_true')
    parser.add_argument('-s', '--solar', help="get solar data", action='store_true')
    parser.add_argument('-p', '--predictions', help="get predictions", action='store_true')

    args = parser.parse_args()

    all_flag = False
    if not args.solar and not args.geomagnetic and not args.predictions:
        all_flag = True

    if args.solar or all_flag:
        print('Solar data:')
        data = get_solar_data()
        for d in data:
            print(d)

    if args.geomagnetic or all_flag:
        print('Geomagnetic data:')
        data = get_geomagnetic_data()
        for d in data:
            print(d)

    if args.predictions or all_flag:
        print('Predictions:')
        data = get_space_weather_predictions()
        for d in data:
            print(d)

if __name__ == "__main__":
    main()
