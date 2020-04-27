# python script for sending message update

import time
import datetime
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
	message = 'ALERT !! FALL DETECTED IN CAM1 AT TIME: ' + str(datetime.datetime.now())

	client = SinchSMS(app_key, app_secret)
	print("Sending '%s' to %s" % (message,  number))

	response = client.send_message(number, message)
	message_id = response['messageId']
	response = client.check_status(message_id)

	# keep trying unless the status retured is Successful
	while response['status'] != 'Successful':
		print(response['status'])
		time.sleep(1)
		response = client.check_status(message_id)

	print(response['status'])

if __name__ == "__main__":
	sendSMS()
