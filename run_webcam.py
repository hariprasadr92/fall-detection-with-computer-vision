import argparse
import logging
import time
import os
import cv2
import numpy as np

# python script for sending message update sms

import time
from time import sleep
from sinchsms import SinchSMS

# function for sending SMS
def sendSMS():

	# enter all the details
	# get app_key and app_secret by registering
	# a app on sinchSMS
	number = '8193293755'
	app_key = 'baf8461b-74c9-402b-badd-83a828820d9c'
	app_secret = 'UNER/xJGN0uM+O3ZA4brOQ=='

	# enter the message to be sent
	message = 'Fall Detected - Patient needs help in room 108'

	client = SinchSMS(app_key, app_secret)
	print("Sending '%s' to %s" % (message, number))

	response = client.send_message(number, message)
	message_id = response['messageId']
	response = client.check_status(message_id)

	# keep trying unless the status retured is Successful
	while response['status'] != 'Successful':
		print(response['status'])
		time.sleep(1)
		response = client.check_status(message_id)

	print(response['status'])


from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh


logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=str, default=0)

    parser.add_argument('--resize', type=str, default='432x368',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=3.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_v2_small', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    
    parser.add_argument('--tensorrt', type=str, default="False",
                        help='for tensorrt process.')
    parser.add_argument('--save_video', type=bool, default="False", help='To write output video. default name file_name_output.avi')
    args = parser.parse_args()
    print(args)

    print("mode 0: Simple pose estimation \n mode 1: People counter \n mode 2: Fall detection\n\n")
    mode = int(input("Select a mode :"))

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    #if w > 0 and h > 0:
    #    print("in if yoyo")
    #    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h), trt_bool=str2bool(args.tensorrt))
    #else:
    #   print("in else yoyo")
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368), trt_bool=str2bool(args.tensorrt))
    #logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    #logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))
    count = 0
    y1 = [1000, 1000]
    y2 = [1000, 1000]
    while True:
        ret_val, image = cam.read()

        #logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)

        #logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

        #logger.debug('show+')
        if mode == 1:
            no_people=len(humans)
            #print(" No. of people: ",no_people)
            cv2.putText(image,
                        "people detected: %d" % (no_people),
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (255, 0, 0), 2)

        elif mode == 2:
            for human in humans:
                for i in range(len(humans)):
                    try:
                        head = human.body_parts[0]
                        chest = human.body_parts[14]
                        #print(head, chest, image.shape[1], image.shape[0])
                        #hx = head.x*image.shape[1]
                        hy = head.y*image.shape[0]
                        #cx = chest.x * image.shape[1]
                        cy = chest.y * image.shape[0]
                        y1.append(hy)
                        y2.append(cy)
                        #print("yoyo", y1, "|", hy)
                        #print("yoyo", y2, "|", cy)
                    except:
                        pass
                    if (((hy-y1[-2]) > 270) and ((cy-y2[-2]) > 270) and (hy-cy <50)):
                        cv2.putText(image, "ALERT! FALL DETECTED !",
                                    (40, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 2, 11)
                        #print("yoyo fall det", hy, "|", cy, "|", y1, "|\n", y2, "|", hy-y1[-2], "|", cy-y2[-2], "|", hy-cy)
                        # for sending sms
                        sendSMS()

        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        fps_time = time.time()
        cv2.imshow('Fall Detection', image)

        #if(frame == 0) and (args.save_video):
        #   out = cv2.VideoWriter(file_write_name+'output.avi',cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 20, (image.shape[1],image.shape[0]))
        #out.write(image)
        k = cv2.waitKey(1) & 0xff
        #print("k value is ", k)
        if k == 27:
            break

        #logger.debug('finished+')

    cv2.destroyAllWindows()
