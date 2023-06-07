'''
  This script is responsible for connecting to the GoPro and recording video once it's within
  a set radius of the given coordinates.
  
  This script runs when the camera should be recording. The "interval" file is used to get
  the recording time chunk in seconds - eg, if "interval" contains "5", the gopro will
  record 5 seconds of video. The video is also encrypted for security. The code is forked
  to have recording and encryption done simultaneously in two processes.
  
  Note that if this code is halted in the middle of a recording, the GoPro will continue
  to record indefinitely and must be manually stopped (though it will hurt nothing if
  the recording continues, the GoPro will simply be on when it doesn't need to be).
'''

# import things
import os
import glob
from signal import signal, SIGINT
from goprocam import GoProCamera, constants
import time
import dronekit
import haversine

# global vars
video_location = os.getcwd() + "videos/"
interval = 3

# for logging, debugging, etc
verbose = True            # print out descriptive text?
logging = True             # log times for recording?
#times = [10, 20, 30, 40]   # seconds to try recording at
#trials = 10                # number of times to do each of above timings
#num_records = 0            # how many times we've recorded

# helper method for connecting to gopro
def handler(s, f):
    gopro.stopWebcam()
    quit()

# removes all files in a given folder
def clean_folder(foldername):
    if verbose:
        print("Clearing directory " + foldername)
    try:
        foldername += "/*" if foldername[-1] != '/' else '*'
        [os.remove(file) for file in glob.glob(foldername, recursive=False)]
    except Exception:
        print("nothing to remove")

# checks if drone_raw_loc (which should be similar to `vehicle.location.global_frame`)
# is at the `origin`, with `radius` (in meters) tolerance
def withinRange(origin, radius, drone_raw_loc):
    if drone_raw_loc.lat is None or drone_raw_loc.lon is None:
        return False
    currentPos = (drone_raw_loc.lat, drone_raw_loc.lon)
    distance = haversine.haversine(origin, currentPos)
    distance = distance * 1000 # convert to meters
    print(f"Location {currentPos}, desired {origin}")
    return distance < radius

# connect to gopro
signal(SIGINT, handler)
gopro = GoProCamera.GoPro(ip_address=GoProCamera.GoPro.getWebcamIP())
gopro.video_settings("480p", fps='30')

# record video based on the time given in file "interval". by default, waits 5 seconds
# before recording to avoid gopro connection errors that would take 12 seconds to resolve
def record_video(sleep=2):
    if verbose:
        print("Recording video for " + str(interval) + "s, wait time of " + str(sleep) + "s")
    try:
        time.sleep(sleep)
        gopro.shoot_video(interval)
    except Exception:
        record_video(sleep=0)

    try:
        gopro.downloadLowRes()
        gopro.delete("all")
    except Exception as e:
        print(e)

# delete old video and key files before recording new ones
clean_folder("videos/encrypted/")

# delete any residual videos
if verbose:
    print("Clearing old GoPro files")
gopro.delete("all")

'''#drone
vehicle = dronekit.connect("/dev/ttyAMA0", baud=57600)

start_rec_location = (38.4342708, -78.856161)

# livelock until we should be recording
in_location = False

while True: #in_location:
    time.sleep(1)
    in_location = withinRange(start_rec_location, 10, vehicle.location.global_frame)
    print(f"In location: {in_location}")
'''

# record forever
while True:
    record_video(2)
