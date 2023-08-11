# Basic Instructions for a Demo

The aim of this document is to provide brief instructions for running a demo with our system. The login for the Jetson Nano is "jetson" "jetson".

## Setting up

It is assumed that you'll be using an access point with both the base LAN server (such as a laptop running Ubuntu) and the UAV's Jetson Nano already connected to the 2.4Ghz network (further range). It's also assumed that the scripts on the base LAN server + the Jetson Nano have the correct IP addresses, credentials, file paths, and etc. already set. Each of the batteries should be fully charged, the UAV should be calibrated, etc. Finally, the base LAN server should have a folder named "test" in the home directory that has the same subfolders as the "test" directory has on the Jetson Nano, being "videos", "images", "emailed-images", "no-detections", and "object-detected".

## Starting a mission

Once these things are set up, running a demo with our system is pretty straightforward. First, go to an area on campus away from buildings with access to a power outlet for the AP. If you are unable to connect the AP to the Internet via Ethernet, emails won't be sent. Hopefully the next version of this system will have cellular connectivity.

Once the AP is turned on, plug in the drone's battery, and make sure the RC is set to "AutoMode" (should be the third switch to the right all the way to the top). The other two modes from middle to bottom are set to "Loiter" and "Land". If this mode isn't correct, the motors can spin the wrong way causing propellers to fly. Once the UAV is on, hold the switch on the GPS to turn off the safety mode.

Next, plug in the Jetson Nano battery, and turn on the GoPro. "USB Connected" should eventually flash on the GoPro's screen. This must be done in this order or the camera won't get an IP address and work with the mission script.

At this point, you should be ready to begin a mission. Use Google Maps (NOT Apple Maps) to decide what coordinates the UAV should go to, as Google Maps uses the correct GPS format for the script. On the base LAN server, start the start-mission.py script with the provided GPS coordinates as arguments on the CLI. From here, the mission should carry out normally, but check our our demo video to see an idea of what the output from a mission looks like.

## If things go sideways during a flight

If anything goes wrong, I'd recommend setting the flight mode with the switch aforementioned to "Land". You could change this in QGC to "RTL" if you wish. Switching to "Loiter" would work too, but make sure the control sticks are centered or the UAV will lose all throttle and fall from the sky. Using a CLI debugger during a flight can be helpful as well if there are issues with a script during a flight.

## Other helpful info

Sometimes, the UAV will ascend into the air and not go anywhere. We think this can be causes by a bad GPS connection, so the best thing to do is land and reboot the UAV. Changing the very last digit of one of the coordinates also fixed the problem.

Try not to fly near buildings as we found they caused GPS interference.
