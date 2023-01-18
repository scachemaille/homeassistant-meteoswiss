# homeassistant-meteoswiss (forked)

Home Assistant meteo swiss integration.

This was forked from https://github.com/websylv/homeassistant-meteoswiss because
the original author is unresponsive.  Use this in your Home Assistant by deleting
the original integration, then adding this as a custom HACS repo, and then
reinstalling the integration through this repository.

## Known issues

None at this time.

## Information

Data from meteo swiss official website

The forecast is extracted from the meteo swiss website

Current conditions are from official data files.

## Installation


## Configuration

- Got to home assistant configuration :

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_br58RnFLHN.png)
  
- Then click on "integrations":

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/jDBoFYSD9L.png)

- Than add a new integration

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_Xu9QUdjj7O.png)
  
- Search for "meteo-swiss"

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_ZAipe8WopB.png)

- By default the integration will try to determine the best settings for you
based on you location:

![enter image description here](https://github.com/websylv/homeassistant-meteoswiss-img/raw/master/mRemoteNG_ZbyekuPQly.png)

If you are not happy with the settings you can update the settings

Meteo Swiss weather station code. This code can be found in : [https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt](https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt)\

  

## Debug

  

In case of problem with the integration

Please open an issue on github with the logs in debug mode.

You need to activate componenent debug log by adding "custom_components.meteo-swiss: debug" to your configuration.yaml

  

```YAML

logger:
default: warning
logs:
[...]
hamsclient.client: debug
custom_components.meteo-swiss: debug

```

  

## Privacy

  

This integration use :

  

https://nominatim.openstreetmap.org for geolocaliation if you don't set you post code

https://data.geo.admin.ch/ for current weather conditions

https://www.meteosuisse.admin.ch for forecast
