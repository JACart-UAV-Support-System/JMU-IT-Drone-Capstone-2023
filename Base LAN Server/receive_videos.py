'''
   This script is intended to receive and decrypt recorded videos from the drone's GoPro. Once these videos are received and decrypted,
   they'll need to be sent to a cloud instance for ML object-detection (and more), but that functionality hasn't been created as of yet.
   
   Currently, this script (along with the corresponding receive_videos.py script on Base LAN server) are written to account for errors
   in transmission, but this functionality isn't fully working yet. The current goal is to detect if a video has been / is being properly
   sent, and if so, discard the incomplete file on both ends and move on to the next recording. However, while this sort-of works,
   the receiving end sometimes gets the wrong name of the next video, or each video that's sent after a failed video can't be properly opened.
   
   There needs to be a check for determining if an .mp4 that has been 'successfully' received is actually readable before sending it off to the
   cloud. Speaking of, since these videos are eventually going to spliced into frames, it may also make sense to split each video into frames,
   save each frame in chronological order to another directory, and have another script encrypt and send these frames to the cloud for object-
   detection instead of sending more videos.
'''

import socket
import os
from Crypto.Cipher import AES

DIR = 'videos/'

# Set up the AES cipher
key = open('secret.key', 'rb').read()
nonce = b'dcd9faad280ea1fcd7702141f2f6ad1e'
cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
 
# Socket server configuration
host = '192.168.1.139'      
port = 12345          
 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)
conn, addr = sock.accept()
print(f'Connection from {addr}')
 
while True:
    data = conn.recv(1024)
    try:
        decoded_data = data.decode()
    except:
        pass
    if decoded_data.endswith("=EOFX="):
        metadata = str(decoded_data).split()
        size = str(metadata[1])
        file_name = str(" ".join(metadata[2:-1]))
        print("-- Receive file: " + file_name + " (" + size + ")")
        file = open(DIR+file_name, 'wb')
        while True:
            data = conn.recv(1024)
            try: 
                if data.decode().endswith('=EOFX=') == True: 
                    break
            except:
                pass
            file.write(cipher.decrypt(data))
        file.close()
        if size == str(os.path.getsize(DIR+file_name)): 
            print(">> Size verified.")
        else: 
            print("!! Size mismatch.")
