PI_BASE_IMG_TAG=v2021.1.4
PHOTONVISION_RELEASE_TAG=v2022.1.6
VENDOR_PREFIX=SnakeEyes
VENDOR_RELEASE=${RELEASE_VERSION}

# Install dependencies
sudo apt install unzip zip sed

# Download new jar from photonvision main repo
curl -sk https://api.github.com/repos/photonvision/photonvision/releases/tags/${PHOTONVISION_RELEASE_TAG} | grep "browser_download_url.*photonvision-.*raspi\.jar" | cut -d : -f 2,3 | tr -d '"' | wget -qi -
JAR_FILE_NAME=$(realpath $(ls | grep photonvision-v.*\.jar))

# Download base image from pigen repo
curl -sk https://api.github.com/repos/photonvision/photon-pi-gen/releases/tags/${PI_BASE_IMG_TAG} | grep "browser_download_url.*zip" | cut -d : -f 2,3 | tr -d '"' | wget -qi -
IMG_FILE_NAME=$(realpath $(ls | grep image_*.zip))

# Config files should be in this repo
HW_CFG_FILE_NAME=$(realpath $(find PhotonVision -name hardwareConfig.json))

# Unzip and mount the image to be updated
unzip $IMG_FILE_NAME
IMAGE_FILE=$(ls | grep *.img)
TMP=$(mktemp -d)
LOOP=$(sudo losetup --show -fP "${IMAGE_FILE}")
sudo mount ${LOOP}p2 $TMP
pushd .

# Copy in the new .jar
cd $TMP/opt/photonvision
sudo cp $JAR_FILE_NAME photonvision.jar

# Copy in custom hardware configuration 
sudo mkdir photonvision_config
cd photonvision_config
sudo cp ${HW_CFG_FILE_NAME} hardwareConfig.json

# Update hardware configuration in place to indicate what release this was
sudo sed -i 's/VENDOR_RELEASE/'"${VENDOR_RELEASE}"'/g' hardwareConfig.json

# Cleanup
popd
sudo umount ${TMP}
sudo rmdir ${TMP}
NEW_IMAGE=$(basename "${VENDOR_PREFIX}-${VENDOR_RELEASE}.img")
mv $IMAGE_FILE $NEW_IMAGE
zip -r $(basename "${VENDOR_PREFIX}-${VENDOR_RELEASE}-image.zip") $NEW_IMAGE
ls
rm $NEW_IMAGE
rm $JAR_FILE_NAME
rm $IMG_FILE_NAME

# make some release notes
touch release_notes.txt
echo "# PhotonVision Raspberry Pi Image for SnakeEyes ${VENDOR_RELEASE}" >> release_notes.txt
echo "Built From:" >> release_notes.txt
echo "  * PhotonVision .jar version ${PHOTONVISION_RELEASE_TAG}" >> release_notes.txt
echo "  * PhotonVision base Raspberry Pi image version ${PI_BASE_IMG_TAG}" >> release_notes.txt
echo "  * SnakeEyes Hardware support files from ${VENDOR_RELEASE}" >> release_notes.txt
echo "" >> release_notes.txt

# Zip up .stl's for release
zip -r snakeyes_case.zip case
