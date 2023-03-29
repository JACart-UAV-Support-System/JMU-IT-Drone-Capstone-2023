'''
   This script is intended to securely send recorded videos from the drone's GoPro as soon as downloaded videos are
   available in the proper directory. The script binds to a remote socket server, checks for the latest video file, encrypts
   the video file with AES shared key (EAX mode), and sends metadata + footage bytes to the Base LAN socket server for decryption.
   
   Currently, this script (along with the corresponding receive_videos.py script on Base LAN server) are written to account for errors
   in transmission, but this functionality isn't fully working yet. The current goal is to detect if a video has been / is being properly
   sent, and if so, discarding the incomplete file on both ends and moving on to the next recording. However, while this sort-of works,
   the receiving end sometimes gets the wrong name of the next video, or each video that's sent after a failed video can't be properly opened.
   I think this is because of the receiving end getting the wrong byte/s to interpret the beginning of the next .mp4 file, but I'll need to
   continue testing to see.
'''

import os
import time
import socket
from Crypto.Cipher import AES

# Set up the AES cipher
key = open('secret.key', 'rb').read()
nonce = b'dcd9faad280ea1fcd7702141f2f6ad1e'
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

# Set up the socket connection
server_address = ('192.168.1.139', 12345)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
print(f'Connected to {server_address}')

# Initialize the last modified time of the video directory
last_modified = None

# Continuously check for new photos
while True:
    # Wait for 1 second before checking for new videos again
    time.sleep(1)

    # Get the latest video added to the directory
    latest_video = None
    for filename in os.listdir('videos/'):
        file_path = os.path.join('videos/', filename)
        if os.path.isfile(file_path):
            if latest_video is None or os.path.getmtime(file_path) > os.path.getmtime(latest_video):
                latest_video = file_path

    # Check if the latest video has been modified since the last check
    try:
        modified_time = os.path.getmtime(latest_video)
    except:
        continue

    if modified_time != last_modified:

        # Encrypt the video and send it to the server
        size = str(os.path.getsize(latest_video))
        metadata = 'FILE: ' + size + ' ' + os.path.basename(latest_video) + ' =EOFX='
        print("- Send file: " + latest_video + " (" + size + "B)")
        sock.send(metadata.encode())
        time.sleep(1)
        try:
            with open(latest_video, 'rb') as f:
                data = f.read()
                data = cipher.encrypt(data)
                # Begin sending file
                sock.sendall(data)
                time.sleep(1)
                sock.send('=EOFX='.encode())
            f.close()
            print('Transfer of ' + latest_video + ' complete.\n')
            os.remove(latest_video)
        except Exception as e:
            print('Error sending file: ' + latest_video + '.\n', str(e))
            continue

