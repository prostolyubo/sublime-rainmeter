# Miniml Skin Suite ![Abandoned](https://img.shields.io/badge/status-abandoned-red.svg)

Minimalist skin suite for [Rainmeter][rainmeter], based on the *illustro* skin suite by [poiru][poiru].

[rainmeter]: http://www.rainmeter.net/ "Rainmeter"
[poiru]: http://poiru.deviantart.com/ "poiru on deviantART"

## Skins

The following skins are included in the suite:

### Clock

Displays the current date and time.

![Clock skin](http://unindented.github.com/miniml-rainmeter/images/Clock.png)

### Disk

Displays the usage of your disks.

Two variants included:

* One disk (`C:\`)
* Two disks (`C:\` and `D:\`)

![Disk skin](http://unindented.github.com/miniml-rainmeter/images/Disk.png)

### Network

Displays your public IP address and network activity.

![Network skin](http://unindented.github.com/miniml-rainmeter/images/Network.png)

### Recycle Bin

Displays the state and size of your recycle bin.

![Recycle Bin skin](http://unindented.github.com/miniml-rainmeter/images/RecycleBin.png)

### System

Displays basic system stats:

* CPU load
* CPU temperature (using the [CoreTemp][coretemp] plugin)
* RAM usage
* SWAP usage.

Two variants included:

* One-core stats
* Two-core stats

![System skin](http://unindented.github.com/miniml-rainmeter/images/System.png)

### Weather

Displays weather information for your location, using the [Weather.com][weathercom] web service.

Four variants included:

* One-day forecast
* Two-day forecast
* Three-day forecast
* Four-day forecast

![Weather skin](http://unindented.github.com/miniml-rainmeter/images/Weather.png)

To specify your location, just modify these URLs in the corresponding `.ini` file:

    ; weather service URL
    urlweb=http://www.weather.com/weather/today/SPXX0050
    urlxml=http://xml.weather.com/weather/local/SPXX0050?cc=*&unit=m&dayf=3

[coretemp]: http://www.alcpu.com/CoreTemp/ "CoreTemp"
[weathercom]: http://www.weather.com/ "Weather.com"

## Meta

* Code: `git clone git://github.com/unindented/miniml-rainmeter.git`
* Home: <https://github.com/unindented/miniml-rainmeter/>

## Contributors

Daniel Perez Alvarez ([unindented@gmail.com](mailto:unindented@gmail.com))

## License

Copyright (c) 2011 Daniel Perez Alvarez ([unindented.org](https://unindented.org/)). This is free software, and may be redistributed under the terms specified in the LICENSE file.
