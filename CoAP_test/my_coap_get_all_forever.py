# charles222, usage: py my_coap_get_test.py --ip 20

import time
#import argparse
import sys
import subprocess

from subprocess import check_output

delay_time 		= 3	#3 seconds
process_timeout = 10

#************************************
# first return:
#			0: OK
#			1: error
#************************************
def ip_address_init():

	global IP_ADDRESS
	global count_resource_number

	try:
		IP_ADDRESS = sys.argv[1]
		count_resource_number = sys.argv[2]
	except:
		print ('Please enter the WiFi IP Address at the end. For example, 192.168.6.106 c     c is to count resource number, n is not') 
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


def get_a_resource_and_count(banner, path):
	print('------------------------------------------- ' + banner + ' ------------------------------------------')

	try:
		f_write = open('coap_temp.txt','w')
		p = subprocess.run("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout, stdout=f_write)
		#p = subprocess.check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout)
		#p = check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout, stdout=f)
		#print (p)
	except:
		print('Time out,', process_timeout, 'seconds expired')
		f_write.close()
		return 1
		
	f_write.close()	
	
	f_read = open('coap_temp.txt','r')
	
	resource_count = 0
	
	for line in f_read:
		if(line.find('Bytes: ') != -1):
			position = line.find('Bytes: ')
			for i in range(position + 7, len(line)):
				if line[i] == ':':
					resource_count += 1
			print('Bytes line length: ', len(line))

	print()
	print('resource count: ',resource_count)
	print()
	f_read.close()
	time.sleep(delay_time)
	
	'''
	for line in f_read:
		if(line.find('Bytes: ') != -1):
			position = line.find('Bytes: ')
			value_start_position = position + 7
			value_end_position = line.find(' ', position + 7)
			value = line[value_start_position: value_end_position]
			print(' ', value)
			return_value.append(value)
	
	time.sleep(delay_time)
	f_read.close()
	return 0
	'''



	
	time.sleep(delay_time)

	
def main():

	if(ip_address_init()):
		return
		
	while 1:
	#if 1:

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
		'''
		if (count_resource_number == 'c'):
			get_a_resource_and_count('GET ALL', '?change=default')
		else:
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

