# homeassistant-meteoswiss (forked)

This is the Meteo Swiss integration for Home Assistant.

## Features

* Interactive setup flow with reasonably good explanations of the
  settings.
* Lets you determine the real-time weather update frequency.
* Lets you customize all entities this integration provides
  (every entity has a unique ID).
* Detects when your real-time weather station has been retired,
  and offers suggestions on how to fix the issue.
* Imports the old Meteo Swiss YAML configuration and alerts
  you to the needed removal of the deprecated YAML.
* Code is much cleaner and works properly.

See below for common issues.

## Installation

*Instructions on migration from the old unmaintained version are below.*

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Add this integration as a custom repository to HACS.  If you use
HACS you already know the generic instructions on how to do this.
Here is how it looks like on the add custom repo screen:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/addcustomrepo.png)

Once added as a custom repository, add the integration to your
HACS setup:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/addrepository.png)

Once done you should see a pending restart box:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/pendingrestart.png)

Restart your Home Assistant:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/restart.png)

Now you are ready to add one or more instances of the integration.

## Setup

- First make sure that your Home Assistant's basic setup (latitude, longitude)
  is correct.  This information is used to help you set up the weather station.
  If, however, it is not correct, you can still override it later.

- Get to the Home Asssistant settings screen:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/settings.png)
  
- Then click on "Devices & Services":

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/devicesservices.png)

- Than add a new integration:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/add.png)
  
- Search for *Meteo Swiss* and then proceed:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/search.png)

- By default the integration will try to determine the best settings for you
  based on your Home zone latitude and longitude:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/latitude.png)

- The next screen will ask you (with a good guess) about your postal code:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/postalcode.png)

- Finally, you get to select the real-time weather station closest to you
  (a good guess is provided) and name your location:

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/weatherstation.png)

- Your task is done and your integration is working.

![enter image description here](https://github.com/Rudd-O/homeassistant-meteoswiss/raw/master/docs/addedandworking.png)

If you are not happy with the settings, in a future release you
will be able to update them.

## Troubleshooting
  
In case of problem with the integration, please open an issue on
[this repository](https://github.com/Rudd-O/homeassistant-meteoswiss)
explaining the issue and attaching the logs in debug mode.

To obtain logs, activate the component debug log in your
`configuration.yaml`, and restarting Home Assistant:

```YAML
logger:
  default: warning
  logs:
    # maybe more stuff here[...]
    hamsclient.client: debug
    hamsclientfork.client: debug
    custom_components.meteo-swiss: debug
```

### Known issues

* Users of older versions of this integration may experience a problem whereby
  the real-time weather sensors provided by the integration don't update,
  and errors on the log appear frequently regarding this issue.  This is caused
  by an older version of the code letting people configure precipitation stations
  as if they were weather stations.  This is no longer possible, but if you
  have this issue, you'll have to upgrade this integration, delete the configuration
  and re-add it — the erroneous station no longer will appear as an option.
* When you upgrade, a number of entities will be created, and a number of other
  entities will be orphaned.  The recommended upgrade path is to delete the
  existing integration, upgrade, restart Home Assistant, and re-add the integration.
  If you don't do this, you will have to delete entities no longer supplied
  by the integration.  This situation is a one-time thing.  The re-setup step
  is necessary because the old integration did not provide unique IDs.
* There is a migration step in the code that is supposed to migrate away
  from `configuration.yaml` setup.  I have not tested it, but you should know
  that this is deprecated.

## Information sources

Data comes from the Meteo Swiss official data sources.
Forecasts are extracted from the Meteo Swiss API.
Current conditions are from official data files.

The real-time data for the stations can be found at https://rudd-o.com/meteostations
(this is a shortlink to it).  Information on the provided values is
available at [https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt](https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/info/VQHA80_en.txt).

### Privacy

This integration uses:

* https://nominatim.openstreetmap.org to guess your post code
* https://data.geo.admin.ch/ for current weather conditions
* https://www.meteosuisse.admin.ch for forecast

## Origins of this work

This was forked from https://github.com/websylv/homeassistant-meteoswiss because
the original author is unresponsive and the original integration was
broken beyond fixing.  Use this in your Home Assistant by deleting
the original integration, then adding this as a custom HACS repo, and
then reinstalling the integration through this repository.

### How to migrate away from websylv's integration

1. First remove any successfully-setup Swiss Meteo integrations.
2. Then remove the integration itself from HACS.
3. Add this one as a custom integration repo in HACS, then install it to your Home Assistant.  See above for installation instructions.
4. Now you can add the integration in Devices & Settings.  See above for setup instructions.
