# charles222, usage: py my_coap_get_test.py --ip 20

import time
#import argparse
import sys
import subprocess

from subprocess import check_output

delay_time 		= 0		# 3 seconds
process_timeout = 3

#************************************
# first return:
#			0: OK
#			1: error
#************************************
def ip_address_init():

	global IP_ADDRESS

	try:
		IP_ADDRESS = sys.argv[1]
	except:
		print ('Please enter the WiFi IP Address at the end. For example, 192.168.6.106 ') 
		return 1
	return 0

'''		
IP_ADDRESS = '192.168.6.'
parser = argparse.ArgumentParser(description='Get last IP address xxx')
#parser.add_argument("--string", type = str)
parser.add_argument("--ip", type = str)
args = parser.parse_args()
#last_IP = str(args.ip)
last_IP = args.ip
print ("last IP byte is " + last_IP)
'''

def get_a_resource(banner, path):
	print('------------------------------------------- ' + banner + ' ------------------------------------------')
	p = subprocess.run("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout)
	#p = subprocess.check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ":5683/3300/0/5700?change=1", shell=True, timeout=3)
	print (p)
	time.sleep(delay_time)



	
def main():

	if(ip_address_init()):
		return
	#while 1:
	if 1:

		'''	
		print("------------------------------------------- PTU GET PBS ID ------------------------------------------")
		#p = subprocess.run("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ":5683/3300/0/5700/?change=1", shell=True, timeout=3)
		p = subprocess.check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ":5683/3300/0/5700?change=1", shell=True, timeout=3)
		print (p)
		time.sleep(delay_time)
		
		print("------------------------------------------- PTU GET PTX FW Ver --------------------------------------")
		p = check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ":5683/3300/4/5700/?change=1", shell=True).decode()
		print (p)
		time.sleep(delay_time)

		print("------------------------------------------- PTU GET PTX SPEC Ver ------------------------------------")
		p = check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ":5683/3300/5/5700/?change=1", shell=True).decode()
		print (p)
		time.sleep(delay_time)
		'''
		get_a_resource('PTU GET PBS ID', '/3300/0/5700?change=1')
		get_a_resource('PTU GET PTX FW Ver', '/3300/4/5700/?change=1')
		get_a_resource('PTU GET PTX SPEC Ver', '/3300/5/5700/?change=1')
		get_a_resource('PTU GET Detect PRU', '/3300/6/5850/?change=1')
		get_a_resource('PTU GET PRU Number', '/3300/7/5700/?change=1')
		get_a_resource('PTU GET PBS Charge', '/3300/11/5700/?change=1')
		get_a_resource('PTU GET Power', '/3305/0/5700/?change=1')
		get_a_resource('PTU GET Voltage', '/3300/12/5700/?change=1')
		get_a_resource('PTU GET Current', '/3300/16/5700/?change=1')
		get_a_resource('PTU GET Temperature', '/3303/0/5700/?change=1')
		get_a_resource('PTU GET Fault', '/3300/20/5700/?change=1')
		#===============================================================================================================================
		get_a_resource('PRU1 GET ID', '/3300/8/5700/?change=1')
		get_a_resource('PRU2 GET ID', '/3300/9/5700/?change=1')
		get_a_resource('PRU3 GET ID', '/3300/10/5700/?change=1')
		#===============================================================================================================================
		get_a_resource('PRU1 GET Power', '/3305/1/5700/?change=1')
		get_a_resource('PRU1 GET Voltage', '/3300/13/5700/?change=1')
		get_a_resource('PRU1 GET Current', '/3300/17/5700/?change=1')
		get_a_resource('PRU1 GET Temperature', '/3303/1/5700/?change=1')
		get_a_resource('PRU1 GET Fault', '/3300/21/5700/?change=1')
		#===============================================================================================================================
		get_a_resource('PRU2 GET Power', '/3305/2/5700/?change=1')
		get_a_resource('PRU2 GET Voltage', '/3300/14/5700/?change=1')
		get_a_resource('PRU2 GET Current', '/3300/18/5700/?change=1')
		get_a_resource('PRU2 GET Temperature', '/3303/2/5700/?change=1')
		get_a_resource('PRU2 GET Fault', '/3300/22/5700/?change=1')
		#===============================================================================================================================
		get_a_resource('PRU3 GET Power', '/3305/3/5700/?change=1')
		get_a_resource('PRU3 GET Voltage', '/3300/15/5700/?change=1')
		get_a_resource('PRU3 GET Current', '/3300/19/5700/?change=1')
		get_a_resource('PRU3 GET Temperature', '/3303/3/5700/?change=1')
		get_a_resource('PRU3 GET Fault', '/3300/23/5700/?change=1')
		#===============================================================================================================================
		get_a_resource('GET ALL', '?change=default')

	
'''


		print("------------------------------------------- Observe ALL -------------------------------------------")
#p = check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar OBSERVE coap://" + IP_ADDRESS + ":5683?change=default", shell=True).decode()
		check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar OBSERVE coap://" + IP_ADDRESS + ":5683?change=default", shell=True).decode()
#print (p)
		time.sleep(delay_time)
#===============================================================================================================================


		print("------------------------------------------- PTU GET Power test -------------------------------------------")
		p = check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ":5683/3305/0/5700/?change=1", shell=True).decode()
		print (p)
		time.sleep(delay_time)

'''




if __name__ == "__main__":
    main()

