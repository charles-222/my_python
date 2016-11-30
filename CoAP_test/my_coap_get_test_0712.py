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


#########################################
# return:
#		0: OK
#		1: Error
#########################################
def get_a_resource(banner, path, return_value):
	print('----- ' + banner + ':')
	
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
	proc = subprocess.Popen("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True)
	try:
		outs, errs = proc.communicate(timeout=3)
		print (outs)
	except:
		proc.kill()
		outs, errs = proc.communicate()
	'''


#***************************************
#***************************************
def summary_report():
	print()
	
	print('------------------------------ summary report ------------------------------')

	print('On_Off (1:On) : ', end="")
	print(str(on_off).strip('[]\''), end="")
	print()

	print('Lock_Un (0:U) : ', end="")
	print(str(lock_unlock).strip('[]\''), end="")
	print()
	
	print('Allow_B (0:A) : ', end="")
	print(str(allow_block).strip('[]\''), end="")
	print()
	
	print('Spec version  : ', end="")
	print(str(spec_ver).strip('[]\''), end="")
	print()

	print('PRU number    : ', end="")
	print(str(pru_number).strip('[]\''), end="")
	print()

	print('Charge status : ', end="")
	print(str(pbs_charge).strip('[]\''), end="")
	print(' ', end="")
	print('(1:charging; 0:not charging)', end="")
	print()

	

	print()
	print('             ID        power      voltage    current   temperature  fault')

	s1 = str(pbs_id).strip('[]\'')
	s2 = str(ptu_power).strip('[]\'')
	s3 = str(ptu_voltage).strip('[]\'')
	s4 = str(ptu_current).strip('[]\'')
	s5 = str(ptu_temp).strip('[]\'')
	s6 = str(ptu_fault).strip('[]\'')
	print('PTU  : {0:15} {1:10} {2:10} {3:10} {4:10} {5:10}'.format(s1, s2, s3, s4, s5, s6))

	s1 = str(pru1_id).strip('[]\'')
	s2 = str(pru1_power).strip('[]\'')
	s3 = str(pru1_voltage).strip('[]\'')
	s4 = str(pru1_current).strip('[]\'')
	s5 = str(pru1_temp).strip('[]\'')
	s6 = str(pru1_fault).strip('[]\'')
	print('PRU1 : {0:15} {1:10} {2:10} {3:10} {4:10} {5:10}'.format(s1, s2, s3, s4, s5, s6))
	
	print()
	print(' ---> Test Pass.  Test Pass.  Test Pass.')
	print('----------------------------------------------------------------------------')
	print()
	
	
def main():

	global on_off, lock_unlock, allow_block
	global pbs_id, fw_ver, spec_ver, detect_pru, pru_number, pbs_charge, ptu_power, ptu_voltage, ptu_current, ptu_temp, ptu_fault
	global pru1_id, pru2_id, pru3_id
	global  pru1_power, pru1_voltage, pru1_current, pru1_temp, pru1_fault
	
	print()
	
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

		on_off = []
		result = get_a_resource('PTU GET PBS ON_OFF', '/3300/1/5850?change=1', on_off)
		if result:	return

		lock_unlock = []
		result = get_a_resource('PTU GET PBS Lock_UnLock', '/3300/2/5850?change=1', lock_unlock)
		if result:	return

		allow_block = []
		result = get_a_resource('PTU GET PBS Allow_Block', '/3300/3/5700?change=1', allow_block)
		if result:	return
		
		pbs_id = []
		result = get_a_resource('PTU GET PBS ID', '/3300/0/5700?change=1', pbs_id)
		if result:	return

		fw_ver = []
		result = get_a_resource('PTU GET PTX FW Ver', '/3300/4/5700/?change=1', fw_ver)
		if result:	return
		spec_ver = []
		result = get_a_resource('PTU GET PTX SPEC Ver', '/3300/5/5700/?change=1', spec_ver)
		if result:	return
		detect_pru = []
		result = get_a_resource('PTU GET Detect PRU', '/3300/6/5850/?change=1', detect_pru)
		if result:	return
		pru_number = []
		result = get_a_resource('PTU GET PRU Number', '/3300/7/5700/?change=1', pru_number)
		if result:	return
		pbs_charge = []
		result = get_a_resource('PTU GET PBS Charge', '/3300/11/5700/?change=1', pbs_charge)
		if result:	return
		ptu_power = []
		result = get_a_resource('PTU GET Power', '/3305/0/5700/?change=1', ptu_power)
		if result:	return
		ptu_voltage = []
		result = get_a_resource('PTU GET Voltage', '/3300/12/5700/?change=1', ptu_voltage)
		if result:	return
		ptu_current = []
		result = get_a_resource('PTU GET Current', '/3300/16/5700/?change=1', ptu_current)
		if result:	return
		ptu_temp = []
		result = get_a_resource('PTU GET Temperature', '/3303/0/5700/?change=1', ptu_temp)
		if result:	return
		ptu_fault = []
		result = get_a_resource('PTU GET Fault', '/3300/20/5700/?change=1', ptu_fault)
		if result:	return
		#===============================================================================================================================
		pru1_id = []
		result = get_a_resource('PRU1 GET ID', '/3300/8/5700/?change=1', pru1_id)
		if result:	return
		'''
		pru2_id = []
		get_a_resource('PRU2 GET ID', '/3300/9/5700/?change=1', pru2_id)
		pru3_id = []
		get_a_resource('PRU3 GET ID', '/3300/10/5700/?change=1', pru3_id)
		'''
		#===============================================================================================================================
		pru1_power = []
		pru1_voltage = []
		pru1_current = []
		pru1_temp = []
		pru1_fault = []
		result = get_a_resource('PRU1 GET Power', '/3305/1/5700/?change=1', pru1_power)
		if result:	return
		result = get_a_resource('PRU1 GET Voltage', '/3300/13/5700/?change=1', pru1_voltage)
		if result:	return
		result = get_a_resource('PRU1 GET Current', '/3300/17/5700/?change=1', pru1_current)
		if result:	return
		result = get_a_resource('PRU1 GET Temperature', '/3303/1/5700/?change=1', pru1_temp)
		if result:	return
		result = get_a_resource('PRU1 GET Fault', '/3300/21/5700/?change=1', pru1_fault)
		if result:	return
		#===============================================================================================================================
		'''
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

		summary_report()




if __name__ == "__main__":
    main()

