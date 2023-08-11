# Overview

Building on JMU IT's capstone from 2022, our team is working towards integrating the object-detection functionalities of the drone to work with JMU's autonomous cart, aka the JACart. We configured our UAV to receive coordinates for the JACart's location, have the drone fly to those coordinates, start recording a video clip once it's within range, split images from the video, process and email images with detected objects via our YOLOv8 model running on the drone's companion computer, and dump the footage on our base LAN server upon mission completion. 
