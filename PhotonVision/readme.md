# PhotonVision and SnakeEyes

[PhotonVision](https://photonvision.org) is one option for vision processing software which is compatible with SnakeEyes.

# Getting Started

Download the latest [preconfigured SnakeEyes Image](https://github.com/PlayingWithFusion/SnakeEyesDocs/releases).

Flash it onto an SD card [using the same process as recommended by PhotonVision](https://docs.photonvision.org/en/latest/docs/getting-started/installation/sw_install/raspberry-pi.html)

The reset of the [PhotonVision docs](https://docs.photonvision.org/en/latest/index.html) should apply as normal.

# Technical Details

The only modification to PhotonVision required to use SnakeEyes is to ensure the [`hardwareConfig.json`](hardwareConfig.json) file is updated to enable dimmable LED support on pin 13.

In 2024, PhotonVision migrated to using an SQLite database to store settings. Its contents is functionally the same as the `hardwareConfig.json` file. The SnakeEyes preconfigured image includes a small database with the LED's configured, but no cameras or pipelines configured. On PhotonVision's first launch, it will fill out the rest of the details for your model of Pi and camera config.

# Legacy Update Process

While still functional for the 2024 season, this method may be removed in the future. 

First, download the hardware config file, `hardwareConfig.json`. [Click this link](https://raw.githubusercontent.com/PlayingWithFusion/SnakeEyesDocs/master/PhotonVision/hardwareConfig.json), then save the file.

[Follow the instructions for installing PhotonVision.](https://docs.photonvision.org/en/latest/docs/getting-started/installation/coprocessor-image.html#raspberry-pi-installation)

Go to `http://photonvision.local:5800/settings.html`, select Import Settings, and upload `hardwareConfig.json`.

Successful configuration should allow you to see and control the LED brightness from the PhotonVision Settings page:

![hardware config](/img/pv_hwcfg.png)

![LED slider](/img/pv_leds.png)

