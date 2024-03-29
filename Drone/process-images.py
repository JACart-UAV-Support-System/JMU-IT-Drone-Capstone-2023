import os
import time
from shutil import rmtree, move
from ultralytics import YOLO

# Set the root path
root_path = '/set/root/path'

# Deletes the runs/detect/ dir so there additional predict folders aren't generated by YOLOv8, creates a new
# empty one to start with
try: 
    rmtree(os.path.join(root_path, 'runs/'))
except:
    pass
os.makedirs(os.path.join(root_path, 'runs/detect'))

# Set our model to VisDrone weights and create an empty set of processed images
model = YOLO(os.path.join(root_path, 'weights/visdrone-custom-v1.pt'))
processed_images = set()

while True:
    # Wait for a few seconds before processing any images to avoid scripts conflicting
    time.sleep(5)
    
    # Get all images in the received-images directory
    images = sorted(os.listdir(os.path.join(root_path, 'images/')))
    
    # Filter images that have not been processed yet
    images = [img for img in images if img not in processed_images]
    
    # Process each image
    for img in images:
        # Run YOLOv8 Object Detection model with VisDrone weights. Saves the text file with detetions,
        # an additional image with annotations, and makes sure the image is set to the imgsz
        # used when training the model on VisDrone.
        results = model.predict(os.path.join(root_path, f'images/{img}'), save_txt=True, save=True, imgsz=800)
        
        # Check if any objects were detected
        txt_file = os.path.join(root_path, f'runs/detect/predict/labels/{os.path.splitext(img)[0]}.txt')
        if os.path.exists(txt_file):
            print(f'Object/s detected in {img}')
            # Move image and txt files to object-detected directory
            move(os.path.join(root_path, f'runs/detect/predict/{img}'), os.path.join(root_path, f'object-detected/detection-{img}'))
            move(os.path.join(root_path, f'images/{img}'), os.path.join(root_path, f'object-detected/{img}'))
            move(txt_file, os.path.join(root_path, f'object-detected/{os.path.splitext(img)[0]}.txt'))
            print('Images and txt file moved')
        else:
            # Move image with no detections to no-detections dir
            move(os.path.join(root_path, f'images/{img}'), os.path.join(root_path, f'no-detections/{img}'))
            print(f'No objects detected in {img}')

        # Mark image as processed
        processed_images.add(img)
