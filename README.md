# easyi3status-weather

## To Install

    wget https://raw.githubusercontent.com/aecepoglu/easyi3status-weather/master/weather.py -P ~/.config/easyi3status/modules/
    
    wget https://raw.githubusercontent.com/aecepoglu/easyi3status-weather/master/requirements.txt -O /tmp/weather-requirements.txt
    pip3 install -r /tmp/weather-requirements.txt
    rm /tmp/weather-requirements.txt
    
    # update the config
    wget https://raw.githubusercontent.com/aecepoglu/easyi3status-weather/master/config.yaml -O - >> ~/.config/easyi3status/config.yaml
    
    # and restart i3 for the changes to take effect


## Configuration

* `city`: **REQUIRED** city id from [here](http://openweathermap.org/help/city_list.txt)
* `appid`: **REQUIRED** appid [that you can retrieve here](http://openweathermap.org/appid)
* `units`: *metric* or *imperial*
* `language`: a language code from [here](http://openweathermap.org/forecast5#multi). *en* by default
* `minWindSpeed`: if wind speed is greater than this, then its speed and direction will be shown
* `wantedHours`: list of which 3-hour intervals to display. Defaults to `[0,3,6,9,12,15,18,21]`

# TODO

* Be able to toggle between current weather and 3-hour forecast
* ~~Be able to specify which 3-hour intervals to display~~
