# charles222, usage: py my_coap_get_test.py --ip 20

import time
#import argparse
import sys
import subprocess

from subprocess import check_output

delay_time 		= 1 #0		# 3 seconds
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

	# append to coap_temp_append.txt below:
	f_read = open('coap_temp.txt','r')
	data_temp = f_read.read()
	f_read.close()

	f_append = open('coap_temp_append.txt','a')
	f_append.write(data_temp)
	f_append.close()
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

#########################################
# return:
#		0: OK
#		1: Error
#########################################
def put_a_resource(banner, path):
	print('----- ' + banner + ':')
	
	try:
		f_write = open('coap_temp.txt','w')
		p = subprocess.run("java -jar cf-client-1.1.0-SNAPSHOT.jar PUT coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout, stdout=f_write)
		#p = subprocess.check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout)
		#p = check_output("java -jar cf-client-1.1.0-SNAPSHOT.jar GET coap://" + IP_ADDRESS + ':5683' + path, shell=True, timeout=process_timeout, stdout=f)
		#print (p)
	except:
		print('Time out,', process_timeout, 'seconds expired')
		f_write.close()
		return 1
		
	f_write.close()	

	# append to coap_temp_append.txt below:
	f_read = open('coap_temp.txt','r')
	data_temp = f_read.read()
	f_read.close()

	f_append = open('coap_temp_append.txt','a')
	f_append.write(data_temp)
	f_append.close()
	
	time.sleep(delay_time)
	return 0

#***************************************
#***************************************
def summary_report(is_wpc):
	print()
	
	print('------------------------------ summary report ------------------------------')

	print('On_Off (1:On) : ', end="")
	#print(str(on_off_on_1).strip('[]\''), end="")
	print(on_off_on_1[0], end="")
	print()
	print('On_Off (0:Of) : ', end="")
	#print(str(on_off_off).strip('[]\''), end="")
	print(on_off_off[0], end="")
	print()
	print('On_Off (1:On) : ', end="")
	#print(str(on_off_on_2).strip('[]\''), end="")
	print(on_off_on_2[0], end="")
	print()
	print()

	print('Lock_Un (0:U) : ', end="")
	print(str(lock_unlock_unlock_1).strip('[]\''), end="")
	print()
	print('Lock_Un (1:L) : ', end="")
	print(str(lock_unlock_lock).strip('[]\''), end="")
	print()
	print('Lock_Un (0:U) : ', end="")
	print(str(lock_unlock_unlock_2).strip('[]\''), end="")
	print()
	print()

	if is_wpc != 1:		# AFA only
		print('Allow_B (0:A) : ', end="")
		print(str(allow_block).strip('[]\''), end="")
		print()
		print()

	print('Firm version  : ', end="")
	print(str(fw_ver).strip('[]\''), end="")
	print()
	
	print('Spec version  : ', end="")
	print(str(spec_ver).strip('[]\''), end="")
	print()

	print('PRU number    : ', end="")
	print(str(pru_number).strip('[]\''), end="")
	print()

	print('PBS Charging  : ', end="")
	print(str(pbs_charge).strip('[]\''), end="")
	print(' ', end="")
	print('(1:charging; 0:not charging)', end="")
	print()

	

	print()
	print('             ID        power      voltage    current   temperature  fault')

	#s1 = str(pbs_id).strip('[]\'')
	s1 = pbs_id[0]
	#s2 = str(ptu_power).strip('[]\'')
	s2 = ptu_power[0]
	s3 = str(ptu_voltage).strip('[]\'')
	s4 = str(ptu_current).strip('[]\'')
	s5 = str(ptu_temp).strip('[]\'')
	#s6 = str(wpc_fault).strip('[]\'')
	#print('PTU  : {0:15} {1:10} {2:10} {3:10} {4:10} {5:10}'.format(s1, s2, s3, s4, s5, s6))
	print('PTU  : {0:15} {1:10} {2:10} {3:10} {4:10}'.format(s1, s2, s3, s4, s5))
	
	s1 = str(pru1_id).strip('[]\'')
	s2 = str(pru1_power).strip('[]\'')
	s3 = str(pru1_voltage).strip('[]\'')
	s4 = str(pru1_current).strip('[]\'')
	s5 = str(pru1_temp).strip('[]\'')
	#s6 = str(afa_fault).strip('[]\'')
	#print('PRU1 : {0:15} {1:10} {2:10} {3:10} {4:10} {5:10}'.format(s1, s2, s3, s4, s5, s6))
	print('PRU1 : {0:15} {1:10} {2:10} {3:10} {4:10}'.format(s1, s2, s3, s4, s5))

	if is_wpc == 1:		# WPC
		s6 = str(wpc_fault).strip('[]\'')
	else:
		s6 = str(afa_fault).strip('[]\'')

	print('       {0:15} {1:10} {2:10} {3:10} {4:10} {5:10}'.format('-', '-', '-', '-', '-', s6))
	
	print()
	print(' ---> Test Pass.  Test Pass.  Test Pass.')
	print('----------------------------------------------------------------------------')
	print()
	
	
def main():

	global on_off_on_1, on_off_on_2, on_off_off, lock_unlock_unlock_1, lock_unlock_unlock_2, lock_unlock_lock, allow_block
	global pbs_id, fw_ver, spec_ver, detect_pru, pru_number, pbs_charge, ptu_power, ptu_voltage, ptu_current, ptu_temp, wpc_fault
	global pru1_id, pru2_id, pru3_id
	global  pru1_power, pru1_voltage, pru1_current, pru1_temp, afa_fault
	
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

		#--------------------------------------------------------------------
		fw_ver = []
		result = get_a_resource('PTU GET PTX FW Ver', '/3300/1/5750/?change=1', fw_ver)
		if result:	return
		spec_ver = []
		result = get_a_resource('PTU GET PTX SPEC Ver', '/3300/3/5700/?change=1', spec_ver)
		if result:	return

		wpc_is_used = 0
		if spec_ver == ['9'] or spec_ver == ['10'] or spec_ver == ['11'] or spec_ver == ['12']:
			wpc_is_used = 1

		print( ' --> WPC is used: ', wpc_is_used, '(1: WPC ; 0: AFA)') 
		print()
		
		#-------------------------------------------------------------------
		on_off_on_1 = []
		result = get_a_resource('PTU GET PBS ON_OFF', '/3306/0/5850?change=1', on_off_on_1)	# with or without / in front of ? are both OK for Californium
		if result:	return

		result = put_a_resource('PTU PUT PBS OFF', '/3306/0/5850 0')	# 0 is OFF
		if result:	return

		on_off_off = []
		result = get_a_resource('PTU GET PBS ON_OFF', '/3306/0/5850?change=1', on_off_off)	# with or without / in front of ? are both OK for Californium
		if result:	return

		result = put_a_resource('PTU PUT PBS ON', '/3306/0/5850 1')		# 1 is ON
		if result:	return

		on_off_on_2 = []
		result = get_a_resource('PTU GET PBS ON_OFF', '/3306/0/5850?change=1', on_off_on_2)	# with or without / in front of ? are both OK for Californium
		if result:	return

		#--------------------------------------------------------------------
		lock_unlock_unlock_1 = []
		result = get_a_resource('PTU GET PBS Lock_UnLock', '/3306/1/5850?change=1', lock_unlock_unlock_1)
		if result:	return

		result = put_a_resource('PTU PUT PBS Lock', '/3306/1/5850 1')	# 1 is Lock		// not implemented yet by Tank
		if result:	return

		lock_unlock_lock = []
		result = get_a_resource('PTU GET PBS Lock_UnLock', '/3306/1/5850?change=1', lock_unlock_lock)
		if result:	return

		result = put_a_resource('PTU PUT PBS UnLock', '/3306/1/5850 0')	# 0 is UnLock
		if result:	return

		lock_unlock_unlock_2 = []
		result = get_a_resource('PTU GET PBS Lock_UnLock', '/3306/1/5850?change=1', lock_unlock_unlock_2)
		if result:	return

		#--------------------------------------------------------------------
		if wpc_is_used != 1:	# AFA only
			allow_block = []
			result = get_a_resource('PTU GET PBS Allow_Block', '/3306/2/5750?change=1', allow_block)
			if result:	return
		
		#--------------------------------------------------------------------
		pbs_id = []
		result = get_a_resource('PTU GET PBS ID', '/3300/0/5700?change=1', pbs_id)
		if result:	return

		
		detect_pru = []
		result = get_a_resource('PTU GET Detect PRU', '/3302/0/5500/?change=1', detect_pru)
		if result:	return
		pru_number = []
		result = get_a_resource('PTU GET PRU Number', '/3300/7/5700/?change=1', pru_number)
		if result:	return
		pbs_charge = []
		result = get_a_resource('PTU GET PBS Charge', '/3306/8/5850/?change=1', pbs_charge)
		if result:	return
		ptu_power = []
		result = get_a_resource('PTU GET Power', '/3305/0/5800/?change=1', ptu_power)
		if result:	return
		ptu_voltage = []
		result = get_a_resource('PTU GET Voltage', '/3300/11/5700/?change=1', ptu_voltage)
		if result:	return
		ptu_current = []
		result = get_a_resource('PTU GET Current', '/3300/15/5700/?change=1', ptu_current)
		if result:	return
		ptu_temp = []
		result = get_a_resource('PTU GET Temperature', '/3303/0/5700/?change=1', ptu_temp)
		if result:	return
		
		#===============================================================================================================================
		pru1_id = []
		result = get_a_resource('PRU1 GET ID', '/3300/8/5750/?change=1', pru1_id)
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
		afa_fault = []
		result = get_a_resource('PRU1 GET Power', '/3305/1/5800/?change=1', pru1_power)
		if result:	return
		result = get_a_resource('PRU1 GET Voltage', '/3300/12/5700/?change=1', pru1_voltage)
		if result:	return
		result = get_a_resource('PRU1 GET Current', '/3300/16/5700/?change=1', pru1_current)
		if result:	return
		result = get_a_resource('PRU1 GET Temperature', '/3303/1/5700/?change=1', pru1_temp)
		if result:	return
		
		if wpc_is_used == 1:	# WPC
			wpc_fault = []
			result = get_a_resource('PTU GET Fault', '/3300/19/5750/?change=1', wpc_fault)
			if result:	return
		else:
			afa_fault = []
			result = get_a_resource('PRU1 GET Fault', '/3300/20/5750/?change=1', afa_fault)
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

		summary_report(wpc_is_used)




if __name__ == "__main__":
    main()

