#!/usr/bin/env python3
#----------------------------------------------------------------------------
# Copyright (c) 2020 Playing With Fusion. See license.txt for more info.
#
# This is a sample python program for configuring and using the NoIR Camera
# with the WPILibPi Raspberry Pi Image and Playing With Fusion's infrared
# LED hat. 
#
# Results of the processing are visible at http://wpilibpi.local:5805/stream.html
# and in Network Tables.
#----------------------------------------------------------------------------

# General Python Libraries Used
import time
import sys, os, math, collections
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# Computer Vision & Processing Libraries
import numpy as np
import cv2

# FRC Network Tables 
from networktables import *

# GPIO Pin Manipulation
# Note this library only does software PWM, 
# so you may see flickering. So far it hasn't impacted
# vision performance.
# The alternate is to install and use the pigpio or RPIO libraries
# for python, or some alternate mechanism which leverages
# the Pi's hardware PWM to get more stable dimming.
import RPi.GPIO as GPIO




######################################################################
## Configuration Constants - Adjust these as needed
######################################################################
# Global Configuration

# Team Setup
TEAM_NUMBER    = 1736

# Camera Setup
CAPTURE_WIDTH  = 320
CAPTURE_HEIGHT = 240
CAPTURE_FPS    = 90

# Vision Processing Pipeline Configuration
MIN_PIXEL_BRIGHTNESS = 100
MAX_PIXEL_BRIGHTNESS = 255
MIN_CONTOUR_WIDTH_PX = 15
MIN_CONTOUR_AREA_PX  = 20

# Control how bright the LED's are set to
# 0.0 = Off, 1.0 = full on.
LED_BRIGHTNESS = 0.25

# Debug Flags
imgProcPrintDebug = False
webServerPrintDebug = False
drawPixelMask = False
drawContours = True
drawStatsOverlay = True


######################################################################
## Sample Vision Processing Pipeline
######################################################################
class SimpleVisionPipeline():

    def __init__(self):
        ##IR Light & Camera Identification Thresholds (HSV)
        self.lowerBrightness=np.array([0,0,MIN_PIXEL_BRIGHTNESS])
        self.upperBrightness=np.array([255,255,MAX_PIXEL_BRIGHTNESS])
        self.fps = 0


    ###########################################
    # Main Processing Pipeline
    ###########################################
    def process(self, inFrame):

        # Save copy of the input frame. Default to output the same image.
        self.inimg = inFrame
        self.maskoutput = inFrame

        # Find pixels which could be part of a target
        self.pixelFilter()

        # Find contours around candidate pixels
        _, contours, _ = cv2.findContours(self.mask, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

        # Filter contour list to only reasonably-sized ones.
        filteredContours = self.filterContours(contours, MIN_CONTOUR_AREA_PX, MIN_CONTOUR_WIDTH_PX, math.inf)
        
        # Identify target location from the given contour list
        self.detectTarget(filteredContours)

        # Update Network Tables with processing results
        self.updateNTOutputs()

        # Draw debug info on the video output
        self.debugDraw()

        if imgProcPrintDebug:
            self.outputStr = "{},{},{}\n".format(self.targetVisible, self.xval, self.yval)
            print(self.outputStr)

        # Return a modified image for streaming to the website
        return self.maskoutput


    ###########################################
    # Pipeline Step Implementation
    ###########################################
    def pixelFilter(self):
        #Sets image to hsv colors
        hsv = cv2.cvtColor(self.inimg, cv2.COLOR_RGB2HSV)

        #Creates mask based on hsv range
        self.mask = cv2.inRange(hsv, self.lowerBrightness, self.upperBrightness)

    def filterContours(self, input_contours, min_area, min_width, max_width):
        output = []
        for contour in input_contours:
            # Reasonably contours will be in a certain range of widths.
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w>max_width):
                continue

            # Reasonable contours will have a minimum amount of area
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            output.append(contour)

        return output
        

    def detectTarget(self, contourinput):

        self.targetVisible = False
        self.xval = 0
        self.yval = 0

        if contourinput:
            #Simple assumption # 1: Biggest contour must correspond to the target.
            self.contoursSorted = sorted(contourinput, key=cv2.contourArea, reverse=True)
            self.targetContour = self.contoursSorted[0]
            self.targetVisible = True

            #Simple Assumption # 2: The target is "located" at the center of the contour.
            M = cv2.moments(self.targetContour)
            self.xval = M["m10"] / M["m00"]
            self.yval = M["m01"] / M["m00"]


    def debugDraw(self):

        if drawPixelMask:
            self.maskoutput = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)

        if drawContours:
            if(self.targetVisible):
                cv2.drawContours(self.maskoutput,[self.targetContour], -1, (0,255,0), 2)
                cv2.drawContours(self.maskoutput,self.contoursSorted[1:], -1, (0,125,125), 2)
                cv2.circle(self.maskoutput,(int(self.xval),int(self.yval)),3,(20,20,20), -1)
                cv2.circle(self.maskoutput,(int(self.xval),int(self.yval)),1,(0,255,255), -1)

        if drawStatsOverlay:
            printXStr = "X:" + "{:7.2f}".format(self.xval) if self.targetVisible else " "*7
            printYStr = "Y:" + "{:7.2f}".format(self.yval) if self.targetVisible else " "*7
            statsStr = "FPS:{:6.2f}".format(self.fps)
            cv2.rectangle(self.maskoutput, (0,0), (CAPTURE_WIDTH,15),(0,0,0),-1)
            cv2.putText(self.maskoutput, statsStr, (3, 12), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255, 255, 255))  
            cv2.putText(self.maskoutput, printXStr, (100, 12), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255, 255, 255))  
            cv2.putText(self.maskoutput, printYStr, (200, 12), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255, 255, 255))  


    def updateNTOutputs(self):
        ntTable.putNumber("targetX", self.xval)
        ntTable.putNumber("targetY", self.yval)
        ntTable.putNumber("targetVisible", self.targetVisible)

    def setDispFPS(self, fps_in):
        self.fps = fps_in

######################################################################
## Class to wrapper control of the Playing With Fusion IR pi Hat
######################################################################
class SnakeEyesBoardControl():
    LED_PWM_DIM_PIN = 13 

    def __init__(self):
        self.pwmNormCMD = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PWM_DIM_PIN, GPIO.OUT)
        self.ledCtrl = GPIO.PWM(self.LED_PWM_DIM_PIN,800)
        self.ledCtrl.start(0)

    def _update(self):
        if(self.pwmNormCMD > 1.0):
            self.pwmNormCMD = 1.0
        elif(self.pwmNormCMD < 0.0):
            self.pwmNormCMD = 0.0
        self.ledCtrl.ChangeDutyCycle(self.pwmNormCMD*100.0)

    """ Public API to set the brightness of the LED Array. 
        0.0 is off, 1.0 is full brightness.
    """
    def setBrightness(self, val):
        self.pwmNormCMD = val
        self._update()

    def shutdown(self):
        self.pwmNormCMD = 0
        self._update()
        self.ledCtrl.stop()
        GPIO.cleanup()




######################################################################
## NOIR-Specific configuration for FRC Vision Processing applications
## Tweak as needed, but hopefully this set is a good start.
######################################################################
def configureNOIRCam():
        print("Configuring NOir Camera...")
        cmdStart="v4l2-ctl --set-ctrl "
        #Turns off Auto setting that would change the ones we put in place
        os.system(cmdStart+"auto_exposure=1")
        os.system(cmdStart+"white_balance_auto_preset=0")

        #User Controls
        os.system(cmdStart+"brightness=30")
        os.system(cmdStart+"contrast=100")
        os.system(cmdStart+"saturation=10")
        os.system(cmdStart+"red_balance=1000")
        os.system(cmdStart+"blue_balance=1000")
        os.system(cmdStart+"horizontal_flip=0")
        os.system(cmdStart+"vertical_flip=0")
        os.system(cmdStart+"power_line_frequency=2")
        os.system(cmdStart+"sharpness=100")
        os.system(cmdStart+"color_effects=0")
        os.system(cmdStart+"rotate=0")
        os.system(cmdStart+"color_effects_cbcr=3896")

        #Codec Controls
        os.system(cmdStart+"video_bitrate_mode=1")
        os.system(cmdStart+"video_bitrate=25000000")
        os.system(cmdStart+"repeat_sequence_header=0")
        os.system(cmdStart+"h264_i_frame_period=60")
        os.system(cmdStart+"h264_level=11")
        os.system(cmdStart+"h264_profile=4")

        #Camera Controls
        os.system(cmdStart+"exposure_time_absolute=93")
        os.system(cmdStart+"exposure_dynamic_framerate=0")
        os.system(cmdStart+"auto_exposure_bias=0")
        os.system(cmdStart+"image_stabilization=0")
        os.system(cmdStart+"iso_sensitivity=0")
        os.system(cmdStart+"iso_sensitivity_auto=0")
        os.system(cmdStart+"exposure_metering_mode=0")
        os.system(cmdStart+"scene_mode=0")

        #JPEG Compression controls
        os.system(cmdStart+"compression_quality=100")



######################################################################
## Simple web-server implementation to stream MJPEG video for
## debug purposes.
######################################################################
class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global img
        if self.path == '/cam.mjpg':
            # Handle requests to see the mjpg stream by sending images as they are available.
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Connection', 'close')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            time.sleep(0.1)
            while True:
                try:
                    if img is not None:
                        _, jpg = cv2.imencode('.jpg', img)
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', str(jpg.size))
                        self.end_headers()
                        sendData = jpg.tostring()
                        self.wfile.write(sendData)
                        self.wfile.write(b'\r\n\r\n')
                        
                        
                except KeyboardInterrupt:
                    print("Keyboard Interrupt Detected")
                    break
                except ConnectionResetError:
                    print("Client Disconnect - Connection Reset")
                    break
                except BrokenPipeError:
                    print("Client Disconnected - Broken Pipe")
                    break

        else:
            
            if self.path == '/':
                self.send_response(301)
                self.send_header('Location', '/stream.html')
                self.end_headers()

            else:

                if self.path == '/stream.html':
                    # Handle requests to see a more friendly stream page with the image on it.
                    webHTMLContent = """<html>
                                        <head></head>
                                        <body>
                                            <img src="cam.mjpg" height="90%"/>
                                        </body>
                                        </html>"""
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.send_header('Content-Length', len(webHTMLContent))
                    self.end_headers()

                else:
                    # Throw 404 at everything else.
                    webHTMLContent = """<html>
                                        <head></head>
                                        <body>
                                            <p> <h1> 404 <br> This page does not exist. <br> Sad panda. </h1> </p>
                                        </body>
                                        </html>"""
                    self.send_response(404)
                    self.send_header('Content-type','text/html')
                    self.send_header('Content-Length', len(webHTMLContent))
                    self.end_headers()

                
                if webServerPrintDebug:
                    print("Serving {} to {}".format(self.path, self.client_address))
                    print(webHTMLContent)

                self.wfile.write(webHTMLContent.encode("utf-8"))
            

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    allow_reuse_address = True
    daemon_threads = True

######################################################################
## Class for tracking performacne of the vision pipeline
######################################################################
class PerformanceTracker():
    def __init__(self):
        self.prevStartTimeSec = 0
        self.curStartTimeSec = 0
        self.curImgRxTimeSec = 0
        self.curEndTimeSec = 0
        self.curFPS = 0
        self.curPipelineDelaySec = 0

        self.NUM_FRAMES_FPS_AVG = 20
        self.fps_avg_buf = collections.deque(maxlen=self.NUM_FRAMES_FPS_AVG)

    def now(self):
        return time.time_ns() / (10 ** 9) # convert to floating-point seconds

    def getCurFPS(self):
        return 1/(self.curStartTimeSec - self.prevStartTimeSec)

    def markLoopStart(self):
        self.prevStartTimeSec = self.curStartTimeSec
        self.curStartTimeSec = self.now()
        self.fps_avg_buf.append(self.getCurFPS())

    def markImgReadDone(self):
        self.curImgRxTimeSec = self.now()

    def markLoopEnd(self):
        self.curEndTimeSec = self.now()

    def getCurFPSAvg(self):
        return sum(self.fps_avg_buf)/float(self.NUM_FRAMES_FPS_AVG)

    def getPlDelay(self):
        return self.curEndTimeSec - self.curImgRxTimeSec



######################################################################
## Main Code Execution Starts Here
######################################################################
if __name__ == "__main__":
    
    #Cross-thread lastest-image sharing
    global img
    img = None
    

    print("PWF Sample NOIR Processing starting")
    print("Python Version {}".format(str(sys.version)))
    print("OpenCV Version: {}".format(cv2.__version__))
    print("numpy Version: {}".format(np.__version__))


    # Set up the NOIR camera to desired settings
    configureNOIRCam()

    # Start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    print("Setting up NetworkTables client for team {}".format(TEAM_NUMBER))
    ntinst.startClientTeam(TEAM_NUMBER)
    ntTable = NetworkTables.getTable("VisionData")

    # Start the Video Capture from the camera
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
    capture.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)

    # Start up the results-view web server
    try:
        server = ThreadedHTTPServer(('wpilibpi.local', 5805), CamHandler)
        t = threading.Thread(target=server.serve_forever)
        t.start()
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()


    leds = SnakeEyesBoardControl()
    leds.setBrightness(LED_BRIGHTNESS) 
    import atexit
    atexit.register(leds.shutdown) #Todo, this is very inelegant but maybe it'll work?

    # Init object to process the camera images
    pl = SimpleVisionPipeline()

    # Init object to track overall pipeline timing performance
    pt = PerformanceTracker()
    

    # Run periodically forever
    print("Vision Processing Starting..")
    while True:     
        pt.markLoopStart()

        # Read next frame from the camera
        rc,cam_img = capture.read() 
        pt.markImgReadDone()

        if not rc:
            img = None
            print("Bad Image Capture!")
            continue
        else:
            img = pl.process(cam_img) # If the captured image was good, run it through the processing

        pl.setDispFPS(pt.getCurFPSAvg())

        time.sleep(0) # Yield to other threads (webserver & streaming)
        pt.markLoopEnd()
