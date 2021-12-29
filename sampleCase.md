# Case

SnakeEyes must be contained within a case for proper functionality. The case must serve a few purposes:

 * Shield the camera from the LED's with opaque material
   * Without this, spill light from the LED's will wash out the image, and made target identification very hard.
* Protect the electronics 

[This case design](https://cad.onshape.com/documents/f103c7ef3fd26794c458b982/w/31e132f18a5a8b15dab352ca/e/fb93b9d1fb39f2f70ae6d80d) is provided as a reference, 3d-printable design for using the SnakeEyes with a Raspberry Pi 3b, 3b+, and 4b. [Download a .zip of the 3d printer reference files here.](https://github.com/PlayingWithFusion/SnakeEyesDocs/releases/latest)

[A video with assembly instructions is provided.](https://youtu.be/iXhFbSNitfY).

Printing in PLA and PETG has been tested. 

> :warning: Be sure to choose a filament color which is opaque to the wavelengths of light being used. Black is a good choice.

After unzipping the .stl files, you will need to export and print the following:

 * 1x `Bottom`
 * 1x `Top`
 * 4x `Main Board Spacer`
 * 1x `Camera Board Spacer Plate`

## Case Additional Components

### Bolts

4x M2.5x25 bolts and nuts are required for assembly. [It was tested with this kit of bolts & nuts.](https://www.amazon.com/gp/product/B082XPZV1V/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)

### Fan

[The case above was designed to fit 25x25x10mm fans, like this one](https://www.amazon.com/gp/product/B01406OSNE/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1). 

## Assembly

### Electronics Prep

Place the SnakeEyes board face-down on your work surface.

Place the `Camera Board Spacer Plate` over the camera mounting holes. 

Position the camera on top of the spacer plate and secure with M2 screws. 

> :bulb: Tighten each bolt to similar tightness to ensure the camera face is not skewed relative to the SnakeEyes main board.

> :warning: Be careful not to over-tighten the bolts and damage the camera printed circuit board.

Connect the camera's ribbon cable to both the camera and the raspberry pi board.

Lightly route the ribbon cable with the required 90deg bend, and two 180deg bends to get it aligned properly to the Raspberry Pi's connector. This is prep work to make it easier to route the cable when assembling the full case.


### Main Case Assembly

Place four M2.5x25 bolts upward through the `Bottom` half of the case.

Slide the Raspberry Pi onto the four bolts.

Place the 4 `Main Board Spacer`s onto the bolts.

Slide the SnakeEyes + Camera assembly onto the bolts.

Press the headers downward to mate the SnakeEyes board to the Pi

> :warning: Carefully push and prod the camera ribbon cable to get it to fit between the boards with minimal pinching.

Place the fan into the holder and connect it to the board-mount jack. Carefully wrap up or route wires away from the camera/LED cluster and the bolts.

Place the `Top` portion of the case over the whole assembly. Push down lightly to compress the spacer/PCB stack. Watch out for pinched wires as you do this - re-route as needed.

Carefully, slide one corner off the edge of the work surface, holding the M2.5 bolt in place with your finger. Place a M2.5 nut into the `Top` portion of the case and twist the bolt to engage it. Repeat for all bolts.

Tighten down all four bolts with an allen wrench. Use a moderate amount of torque: Not enough to strip out your plastic material, but enough to keep the whole structure rigid.

Mount the device to the location on your robot. The outer holes are designed to take 10-24 bolts.
