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
