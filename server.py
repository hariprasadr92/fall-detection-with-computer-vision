import socket
import sys
import cv2
import pickle
import numpy as np
import struct
import zlib
import argparse
import logging
import time
import os
import datetime
# for pose estimation
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

# python script for sending message update sms
import time
from time import sleep
from sinchsms import SinchSMS
import datetime

# function for sending SMS
def sendSMS():
    # enter all the details
    # get app_key and app_secret by registering
    # a app on sinchSMS
    number = '8193293755'
    app_key = 'baf8461b-74c9-402b-badd-83a828820d9c'
    app_secret = 'UNER/xJGN0uM+O3ZA4brOQ=='

    # enter the message to be sent
    message = 'FALERT !! FALL DETECTED IN CAM1 AT TIME: '+ str(datetime.datetime.now())

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


# For OpenPose processing
def fall_detection(image,img_counter):
    global y1
    global y2
    global fps_time
    global hy
    global cy

    print(" APPLOG - Fall detec starts for frame ", img_counter, datetime.datetime.now())
    humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)

    image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

    for human in humans:
        for i in range(len(humans)):
            try:
                head = human.body_parts[0]
                chest = human.body_parts[14]
                hy = head.y * image.shape[0]
                # cx = chest.x * image.shape[1]
                cy = chest.y * image.shape[0]
                y1.append(hy)
                y2.append(cy)
                #print("yoyo", y1, "|", hy)
                #print("yoyo", y2, "|", cy)
                print((hy - y1[-2]),(cy - y2[-2]))
            except:
                pass
            # if ((hy - y1[-2]) > 270) and ((cy - y2[-2]) > 270) and (hy - cy < 50):
            if ((hy - y1[-2]) > 30) or ((cy - y2[-2]) > 30):
                cv2.putText(image, "<FALL DETECTED>",
                            (40, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 2, 11)
                print("yoyo fall det", hy, "|", cy, "|", y1, "|\n", y2, "|", hy - y1[-2], "|", cy - y2[-2], "|",
                      hy - cy)
                # for sending sms
                sendSMS()

    # cv2.putText(image,
    #             "FPS: %f" % (1.0 / (time.time() - fps_time)),
    #             (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             (0, 255, 0), 2)

    # cv2.putText(image, str(img_counter),
    #             (40, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
    #             (0, 0, 255), 2, 11)

    cv2.imshow('Fall Detection', image)
    # fps_time = time.time()


logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

if __name__ == '__main__':

    print(" APPLOG - Main function starts")
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=str, default=0)

    parser.add_argument('--resize', type=str, default='432x368',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=2.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_v2_small',
                        help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')

    parser.add_argument('--tensorrt', type=str, default="False",
                        help='for tensorrt process.')
    parser.add_argument('--save_video', type=bool, default="False",
                        help='To write output video. default name file_name_output.avi')
    args = parser.parse_args()


    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    print(" APPLOG -Model built or loaded")
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368), trt_bool=str2bool(args.tensorrt))
    print(" APPLOG -Pose Estimator loaded ")
    #cam = cv2.VideoCapture(args.camera)
    #ret_val, image = cam.read()
    # logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))
    count = 0
    fps_time = 0
    y1 = [1000, 1000]
    y2 = [1000, 1000]

    HOST = ''
    PORT = 7090
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    img_counter = 0
    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    conn, addr = s.accept()

    data = b""

    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))


    while True:
        while len(data) < payload_size:
            print("Recv: {}".format(len(data)))
            data += conn.recv(1024)

        #print("Done Recv: {}".format(len(data)), img_counter , datetime.datetime.now())
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += conn.recv(1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(zlib.decompress(frame_data), fix_imports=True, encoding="bytes")
        image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        #drive_fall_detection(fall_detection(image))
        if img_counter % 10 == 0:
            fall_detection(image, img_counter)
        print(" APPLOG - Fall detec finshd for frame ", img_counter , datetime.datetime.now())

        img_counter +=1
        #cv2.imshow('ImageWindow', image)
        k = cv2.waitKey(100) & 0xff
        if k == 27:
            break

cv2.destroyAllWindows()


