# PhotonVision and SnakeEyes

[PhotonVision](https://photonvision.org) is one option for vision processing software which is compatible with SnakeEyes.

# Getting Started

[Download and flash the latest version of the PhotonVision Raspberry Pi Image per their instructions.](https://docs.photonvision.org/en/latest/docs/getting-started/installation/coprocessor-image.html#raspberry-pi-installation)

Power the system up, visit the web interface, and ensure you can see the Raspberry Pi camera as the only camera on the system, and can view its stream.

Start by downloading a copy of this [`hardwareConfig.json`](hardwareConfig.json) file. It will configure PhotonVision to use pin 13 as the LED control pin.

Go to the Settings tab, select "Import Settings", and upload the `hardwareConfig.json` file.

The device should restart. After the restart is complete, refresh the webpage.

In the settings page, confirm the "Hardware Model" box now reads `SnakeEyes`. 

Now, the "LEDs" Brightness slider on the settings page should control the LED brightness for SnakeEyes.

After this, all of of [PhotonVision's documentation](https://docs.photonvision.org/en/latest/index.html) applies as normal.
