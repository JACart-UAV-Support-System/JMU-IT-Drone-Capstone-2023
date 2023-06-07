import os
import ssl
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from shutil import move

# Set up Gmail SMTP server with app password for this script. Will update so the credentials aren't
# stored as plaintext
gmail_user = 'REPLACE WITH CAPSTONE EMAIL'
gmail_password = 'REPLACE WITH PASSWORD'
smtp_server = 'smtp.gmail.com'
smtp_port = 587
recipient = 'dkahle8@gmail.com'

# Sets up file paths
src_dir = Path('object-detected')
dst_dir = Path('emailed-images')

# Sets up class names for given class digits to generate subject line
class_dict = {
	0: 'Pedestrian',
	1: 'People',
	2: 'Bicycle',
	3: 'Car',
	4: 'Van',
	5: 'Truck',
	6: 'Tricycle',
	7: 'Awning-tricycle',
	8: 'Bus',
	9: 'Motor',
  10: 'JACart'
}

def emailImages():
	# Find oldest txt file in source directory so the script knows where to start
	txt_files = [f for f in src_dir.glob('*.txt')]
	oldest_txt_file = min(txt_files, key=os.path.getctime)

	# Get corresponding image files for oldest set of images
	image_name = oldest_txt_file.stem
	image_files = [f for f in src_dir.glob(f'{image_name}.jpg')]
	image_files += [f for f in src_dir.glob(f'detection-{image_name}.jpg')]

	# Parse txt file to get class counts
	class_counts = {}
	with open(oldest_txt_file, 'r') as f:
		for line in f:
			class_num = int(line.strip()[0])
			class_name = class_dict[class_num]
			class_counts[class_name] = class_counts.get(class_name, 0) + 1
	
	# Generate email subject line with class detection information
	subject_parts = []
	for class_name, count in class_counts.items():
		subject_parts.append(f'{count} {class_name} Detected')
	subject_line = ', '.join(subject_parts)

	# Create email message
	msg = MIMEMultipart('alternative')
	msg['From'] = gmail_user
	msg['To'] = recipient
	msg['Subject'] = subject_line

	# Add image attachments
	for image_file in image_files:
		with open(image_file, 'rb') as f:
			img_data = f.read()
			img_name = image_file.name
			img_ext = image_file.suffix[1:]  # Remove leading '.' from the file extension
			img_part = MIMEImage(img_data, name=img_name, _subtype=img_ext)  # Specify the image format
			msg.attach(img_part)

	# Encode message as string
	msg_bytes = msg.as_bytes()

	# Send email using Gmail SMTP server with TLS encryption
	context = ssl.create_default_context()
	with smtplib.SMTP(smtp_server, smtp_port) as server:
		server.starttls(context=context)
		server.login(gmail_user, gmail_password)
		server.sendmail(gmail_user, recipient, msg_bytes)
		print("Email sent!")

	# Move files to destination directory so they aren't sent again
	for file in [oldest_txt_file] + image_files:
		time.sleep(1)
		move(file, dst_dir)
		print(f'File {file} moved')
		
	# Wait a few seconds before sending more emails
	time.sleep(5)

# Functionality to allow script to run continuously. If there aren't
# any text files to begin with, the script will wait a few seconds before
# trying to send any more emails.
while True:
	try:
		emailImages()
	except:
		time.sleep(5)
		continue
