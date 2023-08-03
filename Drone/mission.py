from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import os
import sys
import paramiko
import subprocess
import glob
from signal import signal, SIGINT
from goprocam import GoProCamera, constants
import math
import haversine

'''Class and helper methods for copying files from image directory to base server, connecting to GoPro, cleaning folders, checking the location range of the drone,
   and recording video'''

class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise

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
    distance = distance * 1000  # convert to meters
    print(f"Location {currentPos}, desired {origin}")
    return distance < radius

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
        
'''Excecution portion of the script for directing drone to coordinates, recording video clips, saving images from each clip, returning the drone to home, and dumping needed
   files to base server'''
        
# connect to gopro
signal(SIGINT, handler)
gopro = GoProCamera.GoPro(ip_address=GoProCamera.GoPro.getWebcamIP())
gopro.video_settings("1080p", fps='30')

# global vars
video_location = "/video/location/path/videos/"
interval = 10

# for logging, debugging, etc
verbose = True  # print out descriptive text?
logging = True  # log times for recording?
#times = [10, 20, 30, 40]   # seconds to try recording at
#trials = 10                # number of times to do each of above timings
#num_records = 0            # how many times we've recorded

# Get GPS coordinates from command-line arguments
latitude = float(sys.argv[1])
longitude = float(sys.argv[2])

# Connect to the vehicle
vehicle = connect('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0',
                  wait_ready=True, baud=921600)

# Arm and takeoff to a target altitude
target_altitude = 10 # in meters
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True
vehicle.simple_takeoff(target_altitude)

# Wait until the vehicle reaches the target altitude
while True:
    current_altitude = vehicle.location.global_relative_frame.alt
    if current_altitude >= target_altitude * 0.95:
        break
    time.sleep(1)

point = LocationGlobalRelative(latitude, longitude, target_altitude)
print("Heading to given point")

# Go to the specified GPS coordinates
vehicle.simple_goto(point)

# delete old video and image files before recording new ones
clean_folder("/video/location/path/videos/")
clean_folder("/video/location/path/images/")

# delete any residual videos
if verbose:
    print("Clearing old GoPro files")
gopro.delete("all")

# livelock until we should be recording
in_location = False

# checks to see if vehicle is in location
start_rec_location = (latitude, longitude)
while not in_location:
    in_location = withinRange(start_rec_location, 10, vehicle.location.global_frame)
    time.sleep(1)

# once vehicle is within radius, will record 10 second clip
if in_location == True:
    print(f"In location: {in_location}")
    record_video(2)
    
# Save 10 frames from recorded video
video_files = glob.glob(video_location + "*.MP4")
for video_file in video_files:
    duration = subprocess.check_output(["ffprobe", "-i", video_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=%s" % ("p=0")])
    duration = float(duration)
    frame_count = 20  # Number of frames to extract
    time_interval = duration / (frame_count + 1)  # Time interval between frames

    output_folder = os.path.join('/home/jetson/test/images')
    output_filename = os.path.basename(video_file)[:-4]

    subprocess.run([
        "ffmpeg", "-i", video_file, "-vf", f"fps=1/{time_interval}",
        "-q:v", "2", "-f", "image2",
        f"{os.path.join(output_folder, output_filename)}_%02d.jpg"
    ])

# Return to launch
vehicle.mode = VehicleMode("RTL")
print("Returning to launch")
vehicle.close()

# Copy files to remote host via SSH using key authentication
ssh = paramiko.Transport(("REPLACE", REPLACE))

# Load private key
private_key_path = "/key/location/path/key"
private_key = paramiko.RSAKey.from_private_key_file(private_key_path, 'daviddavid')

# Connect to remote host using key authentication
ssh.connect(username="david", pkey=private_key)

# Copy files using SCP
sftp = MySFTPClient.from_transport(ssh)
sftp.put_dir("/local/video/path/videos/", "/remote/video/path/videos/")
sftp.put_dir("/local/video/path/images/", "/local/video/path/images/")
print("Images and files transferred to base server")
sftp.close()
ssh.close()