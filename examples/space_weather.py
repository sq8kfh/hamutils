from hamutils.space_weather import get_space_weather_predictions, get_solar_data, get_geomagnetic_data

print('space_weather_predictions:\n%s\n' % get_space_weather_predictions())
print('solar_data:\n%s\n' % get_solar_data())
print('geomagnetic_data:\n%s' % get_geomagnetic_data())
