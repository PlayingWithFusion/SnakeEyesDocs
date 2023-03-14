#!/bin/bash

PI_BASE_IMG_TAG=v2023.1.3_arm64
PHOTONVISION_RELEASE_TAG=v2023.1.2
VENDOR_PREFIX=SnakeEyes
VENDOR_RELEASE=${RELEASE_VERSION}

# Install dependencies
echo "Updating Dependencies..."
sudo apt install xz-utils sed zip

# Download new jar from photonvision main repo
echo "Downloading specified photonvision .jar..."
curl -v -sk https://api.github.com/repos/photonvision/photonvision/releases/tags/${PHOTONVISION_RELEASE_TAG} | grep "browser_download_url.*photonvision-.*linuxarm64\.jar" | cut -d : -f 2,3 | tr -d '"' | wget -qi -
JAR_FILE_NAME=$(realpath $(ls | grep photonvision-v.*\.jar))

# Download base image from pigen repo
echo "Downloading specified base pi image..."
curl -v -sk https://api.github.com/repos/photonvision/photon-pi-gen/releases/tags/${PI_BASE_IMG_TAG} | grep "browser_download_url.*xz" | cut -d : -f 2,3 | tr -d '"' | wget -qi -
IMG_FILE_NAME=$(realpath $(ls | grep image_*.xz))

# Config files should be in this repo
HW_CFG_FILE_NAME=$(realpath $(find PhotonVision -name hardwareConfig.json))

# Unzip and mount the image to be updated
echo "Unzipping and mounting pi image..."
xz -v --decompress $IMG_FILE_NAME
IMAGE_FILE=$(ls | grep *.img)
TMP=$(mktemp -d)
LOOP=$(sudo losetup --show -fP "${IMAGE_FILE}")
sudo mount ${LOOP}p2 $TMP
pushd .

# Copy in the new .jar
echo "Copying in vendor support files..."
cd $TMP/opt/photonvision
sudo cp $JAR_FILE_NAME photonvision.jar

echo "Jar updated! Creating service..."

pushd .
cd $TMP/etc/systemd/system/multi-user.target.wants
sudo bash -c "printf \
\"[Unit]
Description=Service that runs PhotonVision

[Service]
WorkingDirectory=/opt/photonvision
ExecStart=/usr/bin/java -Xmx512m -jar /opt/photonvision/photonvision.jar
ExecStop=/bin/systemctl kill photonvision
Type=simple
Restart=on-failure
RestartSec=1

[Install]
WantedBy=multi-user.target\" > photonvision.service"
popd

# Copy in custom hardware configuration
sudo mkdir photonvision_config
cd photonvision_config
sudo cp ${HW_CFG_FILE_NAME} hardwareConfig.json

# Update hardware configuration in place to indicate what release this was
sudo sed -i 's/VENDOR_RELEASE/'"${VENDOR_RELEASE}"'/g' hardwareConfig.json

# Cleanup
echo "Re-zipping updated image..."
popd
sudo umount ${TMP}
sudo rmdir ${TMP}
NEW_IMAGE=$(basename "${VENDOR_PREFIX}-${VENDOR_RELEASE}.img")
mv $IMAGE_FILE $NEW_IMAGE
xz -v -z $NEW_IMAGE
mv $NEW_IMAGE.xz $(basename "${VENDOR_PREFIX}-${VENDOR_RELEASE}-image.xz")

echo "Cleaning up..."
rm $JAR_FILE_NAME

# make some release notes
touch release_notes.txt
echo "# PhotonVision Raspberry Pi Image for SnakeEyes ${VENDOR_RELEASE}" >> release_notes.txt
echo "Built From:" >> release_notes.txt
echo "  * PhotonVision .jar version ${PHOTONVISION_RELEASE_TAG}" >> release_notes.txt
echo "  * PhotonVision base Raspberry Pi image version ${PI_BASE_IMG_TAG}" >> release_notes.txt
echo "  * SnakeEyes Hardware support files from ${VENDOR_RELEASE}" >> release_notes.txt
echo "" >> release_notes.txt

