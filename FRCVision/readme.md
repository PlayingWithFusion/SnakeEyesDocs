# FRCVision and SnakeEyes

This sample code runs on the FRC Vision Raspberry Pi Image, and performs basic image processing on an IR camera, as well as interfaces with an LED & power supply hat from Playing With Fusion.

The sample code assumes the Raspberry Pi NOIR camera is in use, and no other cameras are attached to the system.

# Getting Started

## Code

Download a copy of the sample [`snakeEyesVision.py`](snakeEyesVision.py) script. Modify the `TEAM_NUMBER` variable to match your team, along with other configuration as needed.

## Upload

[Download and flash the latest version of the FRCVision Raspberry Pi Image per their instructions.](https://docs.wpilib.org/en/stable/docs/software/vision-processing/raspberry-pi/installing-the-image-to-your-microsd-card.html)

Power the system up, visit the web interface, and ensure you can see the Raspberry Pi camera as the only camera on the system, and can view its stream.

[Reference the Vision Workflows documentation](https://docs.wpilib.org/en/stable/docs/software/vision-processing/raspberry-pi/the-raspberry-pi-frc-console.html#vision-workflows) to upload your modified `snakeEyesVision.py`.

> :bug: To debug, you can change to the `Vision Status` tab, and ensure you have messages indicating the vision processing logic has started.

Once the code is running, visit [`frcvision.local:5805`](http://frcvision.local:5805) in a web browser to see a stream of the processed camera data and some stats.

You can read the target information from Network Tables values `targetX`, `targetY`, and `targetVisible`.

