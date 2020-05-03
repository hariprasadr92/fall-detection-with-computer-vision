# Human fall detection with computer vision
Client-server model to detect human fall detection using OpenPose computer vision library

## About project 
This is a simple project that I created when I explored computer vision using Open CV. It uses OpenPose for detecting human like figure in your video feed.

This is a client-server model ( client records and sends []using TCP] video to server for processing). I tested it over WLAN. Explore futher if your requirements demand more.



## Pre-requisites and installation 

* You need python installed.
* You will need to install tensorflow. 
* You cant install cv2 library. Instead install "opencv-python". Other dependancies should be easy to figure out.
* OpenPose is the library used. Refer to the youtube series below for setup instructions. ( https://www.youtube.com/watch?v=4FZrE3cmTPA 3 videos from here) -- This is the :sweat_smile: toughest part of project. Setting up OpenPose.
* Place the project files in the folder [ pose\tf-pose-estimation ]
* You can alter the fall detection logic as you needed by tweaking the code.

* The cam that needs to be used can be configured in OpenCV function.
* Check firewall settings for server if you use the project in the second way.
* client file should be run from command prompt. It might not by default work if u run it from pycharm or any editor.

-------
Now the ball is in your court. <br>
### Enjoy ! Explore ! Cheers !

--------

