# PhotonVision and SnakeEyes

[PhotonVision](https://photonvision.org) is one option for vision processing software which is compatible with SnakeEyes.

# Getting Started

First, download the hardware config file, `hardwareConfig.json`. [Click this link](https://raw.githubusercontent.com/PlayingWithFusion/SnakeEyesDocs/master/PhotonVision/hardwareConfig.json), then save the file.

<a id="raw-url" href="https://raw.githubusercontent.com/PlayingWithFusion/SnakeEyesDocs/master/PhotonVision/hardwareConfig.json">Download the file from here</a>


[Follow the instructions for installing PhotonVision.](https://docs.photonvision.org/en/latest/docs/getting-started/installation/coprocessor-image.html#raspberry-pi-installation)

Go to `http://photonvision.local:5800/settings.html`, select Import Settings, and upload `hardwareConfig.json`.

All the reset of the [PhotonVision docs](https://docs.photonvision.org/en/latest/index.html) should apply as normal.

Successful configuration should allow you to see and control the LED brightness from the PhotonVision Settings page:

![hardware config](/img/pv_hwcfg.png)

![LED slider](/img/pv_leds.png)

# Technical Details

The only modification to PhotonVision required to use SnakeEyes is to ensure the [`hardwareConfig.json`](hardwareConfig.json) file is updated to enable dimmable LED support on pin 13.

