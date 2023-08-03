import sys
import paramiko
import time

# Get GPS coordinates from command-line arguments
latitude = sys.argv[1]
longitude = sys.argv[2]

# SSH connection details
host = "REPLACE"
username = "REPLACE"
private_key_path = "/private/key/path/key"

# Load private key
private_key = paramiko.RSAKey.from_private_key_file(private_key_path, 'daviddavid')

# Establish SSH connection using private key
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, pkey=private_key)

# Open a new channel with the server and execute the command
channel = ssh.invoke_shell()
channel.send(f"cd ~/test/videos && python3 ~/test/mission.py {latitude} {longitude}\n")

# Continuously read from the channel until it's closed
while not channel.exit_status_ready():
    # Only print data if there is data to read in the channel
    if channel.recv_ready():
        print(channel.recv(1024).decode('utf-8'))

# Delay before closing the client
time.sleep(1)

# Close SSHClient
ssh.close()