
# todo:  read COM port from command line

import time
import serial           	# import the module
import sys
import msvcrt as ms_com		# for MicroSoft. https://docs.python.org/2/library/msvcrt.html

#is_WPC_device		= 1		# test WPC product ********************************



#************************************
# first return:
#			0: OK
#			1: error
#************************************
def com_port_init():

	global ComPort		#************************ use global
	
	try:
		com_num_input = sys.argv[1]
	except:
		print ('Please enter the COM port number at the end. For example, 8, if COM8 is used') 
		return 1

	com_port = 'COM' + str(com_num_input)

	READ_SERIAL_TIMEOUT 	= 5  	# 3 seconds
	try:
		ComPort = serial.Serial(com_port)	#('COM8') # open COM8
		ComPort.baudrate 	= 115200 	# set Baud rate to 115200
		ComPort.bytesize 	= 8    		# Number of data bits = 8
		ComPort.parity   	= 'N'  		# No parity
		ComPort.stopbits 	= 1    		# Number of Stop bits = 1
		ComPort.timeout		= READ_SERIAL_TIMEOUT		# 0.5 second timeout for read(), see http://pyserial.readthedocs.io/en/latest/pyserial_api.html
	except:
		print ('the COM port you enter is not available') 
		return 1
		
	return 0	

COMMAND_TIME_OUT_TIME 	= 10  	#10		# 10 second
wait_time 				= 0.1 	#0.1		# second, ENE need 100 ms delay between two commands

# PTU vs PRU
IS_PTU				= 0x00
IS_PRU				= 0x01
DONT_CARE			= 0xDD		# for other response like Spec Version

# for not found response
IS_POWER_NOT_FOUND				= 0x00
IS_VOLTAGE_NOT_FOUND			= 0x01
IS_CURRENT_NOT_FOUND			= 0x02
IS_TEMPERATURE_NOT_FOUND		= 0x03
IS_PRX_ID_NOT_FOUND				= 0x04

# for PRU_ID number
ZERO_PRU_ID			= 0x00
ONE_PRU_ID			= 0x01

# for version number
FIRST_TIME_VERSION	= 0x00
LATER_TIME_VERSION	= 0x01

# for PBS start/stop charge
START_CHARGE		= 0x00
STOP_CHARGE			= 0x01

# for command's Opcode
ASK_ON				= 0x01
ASK_OFF				= 0x02
ASK_LOCK			= 0x03
ASK_UNLOCK			= 0x04

ASK_FW_VER			= 0x07
ASK_SPEC_VER		= 0x08

ASK_POWER			= 0x09
ASK_VOLTAGE			= 0x0A
ASK_CURRENT			= 0x0B
ASK_TEMPERATURE		= 0x0C
ASK_PRU_ID			= 0x0D

ACK_PRXID			= 0x8E
NOT_FOUND			= 0x8F

DETECT_PRX     		= 0x90
PBS_CHARGE     		= 0x91
PRU_CHARGE_START 	= 0x92
PRU_CHARGE_STOP 	= 0x93
FAULT_AUTO		 	= 0x94
PBS_RESTART_AUTO	= 0x95

class PXU_Readings:			# for both PTU and PRU
	power = -1
	voltage = -1
	current = -1
	temp = -127

fw_ver 				= []
spec_ver			= []

ptu_read_start 				= PXU_Readings()
ptu_read_on_with_pru 		= PXU_Readings()
ptu_read_lock_with_pru		= PXU_Readings()
ptu_read_off_no_pru 		= PXU_Readings()
ptu_read_off_with_pru 		= PXU_Readings()
#ptu_read_after_pru_removal 	= PXU_Readings()

pru_read_on 				= PXU_Readings()
pru_read_lock 				= PXU_Readings()
#pru_read_after_removal 		= PXU_Readings()


def print_seperation_line():
	print('=================================================================')
	
#*******************************************************
# wait up to READ_SERIAL_TIMEOUT * 10 = 10 seconds
# tx_data: payload to be sent
# return: no return
#*******************************************************
def command_tx(cmd_tx, tx_data, cmd_name):
	tx_list = []
	checksum = 0
	return_value = 0

	#-------------------------------- write ----------------------------
	tx_list.append(0xA5)
	tx_list.append(0xA5)
	tx_list.append(cmd_tx)
	for i in range(0, 6):
		tx_list.append(tx_data[i])
	for i in range(0, 9):
		checksum += tx_list[i]
	checksum %= 256
	tx_list.append(checksum)
	No = ComPort.write(bytearray(tx_list))
	
	print(cmd_name, 'Command sent:     ', end="")
	#print(tx_list[0:10])
	for i in range(0, 10):
		print(format(tx_list[i], '02X'), end="")	# or   print('{0:2X}'.format(tx_list[i]), end="")
		print(' ', end="")
	print()



#*******************************************************
# wait up to READ_SERIAL_TIMEOUT * 10 = 10 seconds
# tx_data: payload to be sent
# pxu: can be PTU or PRU. Need to check received data (rx_list[8]) based on PTU or PRU
# return_data: received payload data (6 bytes), must pass in an empty list ( [] )
# return:
#		  	0: OK
#			1: error
#*******************************************************
def command_tx_rx(cmd_tx, tx_data, pxu, return_data, cmd_name):
	tx_list = []
	checksum = 0
	return_value = 0

	#-------------------------------- write ----------------------------
	tx_list.append(0xA5)
	tx_list.append(0xA5)
	tx_list.append(cmd_tx)
	for i in range(6):	#range(0, 6):
		tx_list.append(tx_data[i])
	for i in range(9):	#range(0, 9):
		checksum += tx_list[i]
	checksum %= 256
	tx_list.append(checksum)
	No = ComPort.write(bytearray(tx_list))
	
	print(cmd_name, 'Command sent:     ', end="")
	#print(tx_list[0:10])
	for i in range(10):	#range(0, 10):
		print(format(tx_list[i], '02X'), end="")
		print(' ', end="")
	print()
	

	#-------------------------------- read ----------------------------
	rx_list = []
	checksum = 0
	#data = ComPort.readline()        	# Wait and read data, need 0D 0A
	for i in range(0, 10):				# read 10 bytes
		data = ComPort.read()        	# Wait and read data, one byte. If timeout, return 0x00 to data
		#print(type(data))				# data is <class 'bytes'>
		rx_list.append(int.from_bytes(data, byteorder='big'))
	for i in range(0, 9):	
		checksum += rx_list[i]
	checksum %= 256
	print(cmd_name, 'Command Response: ', end="")
	#print(rx_list[0:10])
	for i in range(0, 10):
		print(format(rx_list[i], '02X'), end="")
		print(' ', end="")
	print()
	#print('Rx checksum calculated is:', format(checksum, '02X'))
	if ((rx_list[0] == 0x5A) and (rx_list[1] == 0x5A) and (rx_list[2] == cmd_tx + 0x80) and rx_list[9] == checksum):
		if pxu == IS_PTU:
			if rx_list[8] == 0x00:
				print('-->', cmd_name, 'Response is correct')
			else:
				print('-->', cmd_name, 'Response is wrong --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
				return_value = 1
		elif pxu == IS_PRU:
			if rx_list[8] == 0x01:
				print('-->', cmd_name, 'Response is correct')
			else:
				print('-->', cmd_name, 'Response is wrong --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
				return_value = 1
		else:	# don't care
			print('-->', cmd_name, 'Response is correct')
	else:
		print('-->', cmd_name, 'Response is wrong --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
		return_value = 1

	print_seperation_line()
	#print(' ')

	for i in range(0, 6):
		return_data.append(rx_list[i + 3])
	
	return return_value



#*******************************************************
# send query command and expect to get "not found" response
# wait up to READ_SERIAL_TIMEOUT * 10 = 10 seconds
# tx_data: payload to be sent
# type: IS_POWER_NOT_FOUND, IS_VOLTAGE_NOT_FOUND, IS_CURRENT_NOT_FOUND, IS_TEMPERATURE_NOT_FOUND
# return:
#		  	0: OK
#			1: error
#*******************************************************
def command_tx_rx_not_found(cmd_tx, tx_data, type, cmd_name):
	tx_list = []
	checksum = 0
	return_value = 0

	#-------------------------------- write ----------------------------
	tx_list.append(0xA5)
	tx_list.append(0xA5)
	tx_list.append(cmd_tx)
	for i in range(0, 6):
		tx_list.append(tx_data[i])
	for i in range(0, 9):
		checksum += tx_list[i]
	checksum %= 256
	tx_list.append(checksum)
	No = ComPort.write(bytearray(tx_list))
	
	print(cmd_name, 'Command sent:     ', end="")
	#print(tx_list[0:10])
	for i in range(0, 10):
		print(format(tx_list[i], '02X'), end="")
		print(' ', end="")
	print()
	

	#-------------------------------- read ----------------------------
	rx_list = []
	checksum = 0
	#data = ComPort.readline()        	# Wait and read data, need 0D 0A
	for i in range(0, 10):				# read 10 bytes
		data = ComPort.read()        	# Wait and read data, one byte. If timeout, return 0x00 to data
		#print(type(data))				# data is <class 'bytes'>
		rx_list.append(int.from_bytes(data, byteorder='big'))
	for i in range(0, 9):	
		checksum += rx_list[i]
	checksum %= 256
	print(cmd_name, 'Command Response: ', end="")
	#print(rx_list[0:10])
	for i in range(0, 10):
		print(format(rx_list[i], '02X'), end="")
		print(' ', end="")
	print()
	#print('Rx checksum calculated is:', format(checksum, '02X'))
	if ((rx_list[0] == 0x5A) and (rx_list[1] == 0x5A) and (rx_list[2] == NOT_FOUND) and rx_list[9] == checksum and  rx_list[8] == type):
		print('-->', cmd_name, 'Response Not Found is correct')
	else:
		print('-->', cmd_name, 'Response Not Found is wrong --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
		return_value = 1

	print_seperation_line()
	#print(' ')
	
	return return_value


#*********************************************
# return the valid command received
# return_command is passed in as an empty list ([])
# wait for a_time seconds
# return:
#		0: OK
#		1: timeout or fail
#*********************************************
def get_a_valid_command(return_command, a_time):
	response_found = 0
	response_length = 0
	response_list = []

	timeout = time.time() + a_time
	
	while (response_found == 0):
		if time.time() > timeout:
			return 1
			
		time.sleep(0.05)	# save CPU time
		
		data = ComPort.read()		#If timeout, return 0x00 to data
		data_int = int.from_bytes(data, byteorder='big')
		
		#print(format(data_int, '02X'), end="")
		#print(' ', end="")
		
		if(response_length == 0):
			#print('1')
			if(data_int == 0x5A):
				header_5A_found = 1
				response_list.append(data_int)
				response_length += 1
		elif(response_length == 1):
			#print('2')
			if(data_int == 0x5A):
				header_5A_5A_found = 1
				response_list.append(data_int)
				response_length += 1
			else:
				response_list = []
				response_length = 0
		elif(response_length == 9):	 #checksum byte is received now
			#print('3')
			response_list.append(data_int)
			response_length += 1
			checksum = 0
			for i in range(0, 9):
				checksum += response_list[i]
			checksum %= 256
			if(checksum == data_int):
			  	response_found = 1
			else:
				response_list = []
				response_length = 0
		else:
			#print('4')
			response_list.append(data_int)
			response_length += 1
			
	for i in range(10):	
		return_command.append(response_list[i])
		
	print('valid Command found: ', end="")
	for i in range(10):
		print(format(response_list[i], '02X'), end="")
		print(' ', end="")

	print()
	#print('==================================================')
	#print()
	return 0


#***************************************
# return 0: OK
# return 1: error
#***************************************
def detect_restart_command():
	pbs_restart_received = 0
	while(pbs_restart_received != 1):
		a_response = []
		result = get_a_valid_command(a_response, COMMAND_TIME_OUT_TIME)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to get PBS Restart message')
			return 1	
			
		if(a_response[2] == PBS_RESTART_AUTO):
			pbs_restart_received = 1
			print('--> PBS_RESTART is received, PBS restarts')

	print_seperation_line()
	print(' ')
	return 0

#*********************************************
# Version information
# return:
#		0: OK
#		1: error
#*********************************************
def get_version_info(not_first_time):
	#wait_time = 1	# second
	return_data = []
	error = 0
	wpc_found = 0
	result = command_tx_rx(0x07, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'FW Ver')
	if result == 0:	# OK
		if not_first_time == 0:		# first time
			for i in range(4):
				fw_ver.append(return_data[i + 1])
		else:
			for i in range(4):
				if fw_ver[i] != return_data[i + 1]:
					error = 1
	else:
		error = 1
	time.sleep(wait_time)

	return_data = []
	result = command_tx_rx(0x08, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], DONT_CARE, return_data, 'Spec Ver')
	if result == 0:	# OK
		if not_first_time == 0:		# first time
			if (return_data[5] != 0):	# for WPC device
				wpc_found = 1
			for i in range(2):
				spec_ver.append(return_data[i + 4])
		else:
			for i in range(2):
				if spec_ver[i] != return_data[i + 4]:
					error = 1
			
	else:
		error = 1
	time.sleep(wait_time)

	if not_first_time == 0:		# first time
		return (error, wpc_found)
	else:
		return error


'''
#*********************************************
# compare two list to see if they are equal
# return:
#		0: equal
#		1: otherwise
#*********************************************
def my_cmp(list_a, list_b):
	not_match = 0
	for i in range(6):
		#print( '-->', list_a[i], list_b[i]) 
		if list_a[i] != list_b[i]:
			not_match = 1
			break

	return not_match
'''

#*********************************************
# PTU   PTU   PTU
# return:
#		0: OK
#		1: error
#*********************************************
def get_ptu_readings(reading):
	#wait_time = 1	# second
	return_data = []
	error = 0
	result = command_tx_rx(0x09, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU power')
	if result == 0:	# OK
		reading.power = return_data[0] * 256 + return_data[1]
	else:
		error = 1
	time.sleep(wait_time)

	return_data = []
	result = command_tx_rx(0x0A, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU voltage')
	if result == 0:	# OK
		reading.voltage = return_data[0] * 256 + return_data[1]
	else:
		error = 1
	time.sleep(wait_time)

	return_data = []
	result = command_tx_rx(0x0B, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU current')
	if result == 0:	# OK
		reading.current = return_data[0] * 256 + return_data[1]
	else:
		error = 1
	time.sleep(wait_time)

	return_data = []
	result = command_tx_rx(0x0C, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU temperature')
	if result == 0:	# OK
		reading.temp = return_data[0] * 256 + return_data[1]
	else:
		error = 1
	time.sleep(wait_time)
	return error


#*********************************************
# PTU   PTU   PTU
# return:
#		0: OK
#		1: error
#*********************************************
def test_control_commands(command):
	#wait_time = 1	# second
	return_data = []
	error = 0
	if(command == ASK_OFF):
		result = command_tx_rx(0x02, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU Off')
	elif(command == ASK_ON):	# On
		result = command_tx_rx(0x01, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU On')
	elif(command == ASK_LOCK):	# Lock
		result = command_tx_rx(0x03, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU Lock')
	else:		# UnLock
		result = command_tx_rx(0x04, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU Unlock')
	
	
	if result != 0:
		error = 1
	time.sleep(wait_time)

	return error


#*********************************************
# PTU   PTU   PTU
# send command without checking its response
# return: no return
#*********************************************
def send_command(command):
	#wait_time = 1	# second
	if command == ASK_OFF:
		command_tx(0x02, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU Off')
	elif command == ASK_ON:	# On
		command_tx(0x01, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU On')
	elif command == ASK_LOCK:	# Lock
		command_tx(0x03, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU Lock')
	elif command == ASK_UNLOCK:	# UnLock
		command_tx(0x04, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU Unlock')
	elif command == ASK_PRU_ID:	# ASK_PRU_ID
		command_tx(0x0D, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PRX ID')
	
	time.sleep(wait_time)

	

#*********************************************
# PTU   PTU   PTU
# return:
#		0: OK
#		1: error
#*********************************************
def test_pru_id_command(id_number):
	#wait_time = 1	# second
	return_data = []
	error = 0
	result = command_tx_rx(ASK_PRU_ID, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], DONT_CARE, return_data, 'PRx ID')
	
	if result != 0:	# not OK
		error = 1

	if(return_data[5] != id_number):	# device number should be 0 or 1
		error = 1
		
	return error

#********************************
# PRU   PRU   PRU
# return:
#		0: OK
#		1: error
#********************************
def get_pru_readings(address, reading, is_WPC_device):
	#wait_time = 1	# second
	data = []
	error = 0
	for i in range(0, 5):
		data.append(address[i + 1])
	data.append(IS_PRU)
	
	return_data = []
	result = command_tx_rx(0x09, data, IS_PRU, return_data, 'PRU power')
	if result == 0:	# OK
		reading.power = return_data[0] * 256 + return_data[1]
	else:
		error = 1
	time.sleep(wait_time)

	if(is_WPC_device != 1):
		return_data = []
		result = command_tx_rx(0x0A, data, IS_PRU, return_data, 'PRU voltage')
		if result == 0:	# OK
			reading.voltage = return_data[0] * 256 + return_data[1]
		else:
			error = 1
		time.sleep(wait_time)

		return_data = []
		result = command_tx_rx(0x0B, data, IS_PRU, return_data, 'PRU current')
		if result == 0:	# OK
			reading.current = return_data[0] * 256 + return_data[1]
		else:
			error = 1
		time.sleep(wait_time)

		return_data = []
		result = command_tx_rx(0x0C, data, IS_PRU, return_data, 'PRU temperature')
		if result == 0:	# OK
			reading.temp = return_data[0] * 256 + return_data[1]
		else:
			error = 1
		time.sleep(wait_time)
	
	return error


#********************************
# PRU   PRU   PRU
# readings not found
# return:
#		0: OK
#		1: error
#********************************
def get_pru_readings_not_found(address, is_WPC_device):
	#wait_time = 1	# second
	data = []
	error = 0
	for i in range(0, 5):
		data.append(address[i + 1])
	data.append(IS_PRU)
	
	result = command_tx_rx_not_found(ASK_POWER, data, IS_POWER_NOT_FOUND, 'PRU power')
	if result == 1:	# Fail
		error = 1
	time.sleep(wait_time)

	if is_WPC_device != 1:
		result = command_tx_rx_not_found(ASK_VOLTAGE, data, IS_VOLTAGE_NOT_FOUND, 'PRU voltage')
		if result == 1:	# Fail
			error = 1
		time.sleep(wait_time)

		result = command_tx_rx_not_found(ASK_CURRENT, data, IS_CURRENT_NOT_FOUND, 'PRU current')
		if result == 1:	# Fail
			error = 1
		time.sleep(wait_time)

		result = command_tx_rx_not_found(ASK_TEMPERATURE, data, IS_TEMPERATURE_NOT_FOUND, 'PRU temperature')
		if result == 1:	# Fail
			error = 1
		time.sleep(wait_time)
	
	return error


#****************************************************************************
# detect START charge command from PRU, maybe can detect Detect PRx here too
# return 
#		0: OK
# 		1: error
#****************************************************************************
def detect_start_charge_command_and_pru_addr(address, detect_address):
	pbs_charge_start_received = 0
	pru_charge_start_received = 0

	do_it = 1

	while(do_it == 1):
	#while(pbs_charge_start_received != 1 or pru_charge_start_received != 1):
	#while(pbs_charge_start_received != 1):	# ENE only has this one
		a_response = []
		result = get_a_valid_command(a_response, COMMAND_TIME_OUT_TIME + 10)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME + 10, ' seconds ) to detect PRU on pad')
			return 1
			
		if(a_response[2] == PBS_CHARGE and a_response[8] == START_CHARGE):
			pbs_charge_start_received = 1
			print('--> PBS_CHARGE is received, PBS is charging PRU')
		elif(a_response[2] == PRU_CHARGE_START):
			pru_charge_start_received = 1
			print('--> PRU_CHARGE_START is received, PRU is under charging')
			for i in range(0, 6):
				address.append(a_response[3 + i])
		elif(a_response[2] == DETECT_PRX):
			print('--> DETECT_PRX is received')
			#timeout = time.time()	# no need to wait anymore
			for i in range(0, 6):
				detect_address.append(a_response[3 + i])
		else:
			print('--> unexpected message is received')
			continue	# don't sleep! to speed up

	#if(is_WPC_device == 1):
	#	if(pbs_charge_start_received == 1):
	#		do_it = 0
	#else:
		if(pbs_charge_start_received == 1 and pru_charge_start_received == 1):
			do_it = 0

		time.sleep(2)	# wait 2 seconds to see if other commands in between

				
	print_seperation_line()
	#print(' ')
	return 0


#***************************************
# detect STOP charge command from PRU
# return 0: OK
# return 1: error
#***************************************
def detect_stop_charge_command(address):
	pbs_charge_stop_received = 0
	pru_charge_stop_received = 0
	do_it = 1
	error = 0
	while(do_it == 1):
	#while(pbs_charge_stop_received != 1 or pru_charge_stop_received != 1):
	#while(pbs_charge_stop_received != 1):	# ENE only has this one
		
		a_response = []
		result = get_a_valid_command(a_response, COMMAND_TIME_OUT_TIME)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to detect PRU removal')
			error = 1
		elif(a_response[2] == PBS_CHARGE and a_response[8] == STOP_CHARGE):
			pbs_charge_stop_received = 1
			print('--> PBS_CHARGE is received, PBS stops charging PRU')
		elif(a_response[2] == PRU_CHARGE_STOP):
			for i in range(0, 6):	# compare PRU address
				if(address[i] != a_response[i + 3]):
					print('--> PRU_CHARGE_STOP is received, but PRU address is not matched')
					error = 1
					break
			pru_charge_stop_received = 1
			print('--> PRU_CHARGE_STOP is received, PRU is not under charging')
		elif(a_response[2] == DETECT_PRX):
			print('--> DETECT_PRX is received')
			#timeout = time.time()	# no need to wait anymore
			#for i in range(0, 6):
			#	detect_address.append(a_response[3 + i])
		else:
			print('--> unexpected message is received')
			error = 1
			
	#if(is_WPC_device == 1):
	#	if(pbs_charge_stop_received == 1):
	#		do_it = 0
	#else:
		if(pbs_charge_stop_received == 1 and pru_charge_stop_received == 1):
			do_it = 0
				
		#time.sleep(2)	# wait 2 seconds to see if other commands in between

				
	print_seperation_line()
	#print(' ')
	return error


#***************************************
# detect STOP charge command from PRU
# return 0: OK
# return 1: error
#***************************************
def detect_off_response_and_stop_charge_command(address):
	pbs_charge_stop_received = 0
	pru_charge_stop_received = 0
	off_response_received = 0
	do_it = 1
	error = 0
	while(do_it == 1):
	#while(pbs_charge_stop_received != 1 or pru_charge_stop_received != 1):
	#while(pbs_charge_stop_received != 1):	# ENE only has this one
		
		a_response = []
		result = get_a_valid_command(a_response, COMMAND_TIME_OUT_TIME)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to detect PRU removal')
			error = 1
		elif(a_response[2] == PBS_CHARGE and a_response[8] == STOP_CHARGE):
			pbs_charge_stop_received = 1
			print('--> PBS_CHARGE is received, PBS stops charging PRU')
		elif(a_response[2] == PRU_CHARGE_STOP):
			for i in range(0, 6):	# compare PRU address
				if(address[i] != a_response[i + 3]):
					print('--> PRU_CHARGE_STOP is received, but PRU address is not matched')
					error = 1
					break
			pru_charge_stop_received = 1
			print('--> PRU_CHARGE_STOP is received, PRU is not under charging')
		elif(a_response[2] == DETECT_PRX):
			print('--> DETECT_PRX is received')
			#timeout = time.time()	# no need to wait anymore
			#for i in range(0, 6):
			#	detect_address.append(a_response[3 + i])
		elif(a_response[2] == ASK_OFF + 0x80):
			print('--> OFF response is received')
			off_response_received = 1
			checksum = 0
			for i in range(0, 9):	
				checksum += a_response[i]
			checksum %= 256
			if checksum != a_response[9]:
				error = 1
		else:
			print('--> unexpected message is received')
			error = 1
			
	#if(is_WPC_device == 1):
	#	if(pbs_charge_stop_received == 1):
	#		do_it = 0
	#else:
		if(pbs_charge_stop_received == 1 and pru_charge_stop_received == 1 and off_response_received == 1):
			do_it = 0
				
		#time.sleep(2)	# wait 2 seconds to see if other commands in between

				
	print_seperation_line()
	#print(' ')
	return error





#***************************************
# detect off response
# return 0: OK
# return 1: error
#***************************************
def detect_off_response():

	off_response_received = 0
	do_it = 1
	error = 0
	while(do_it == 1):
	#while(pbs_charge_stop_received != 1 or pru_charge_stop_received != 1):
	#while(pbs_charge_stop_received != 1):	# ENE only has this one
		
		a_response = []
		result = get_a_valid_command(a_response, COMMAND_TIME_OUT_TIME)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to detect PRU removal')
			error = 1
		elif(a_response[2] == ASK_OFF + 0x80):
			print('--> OFF response is received')
			off_response_received = 1
			checksum = 0
			for i in range(0, 9):	
				checksum += a_response[i]
			checksum %= 256
			if checksum != a_response[9]:
				error = 1
		else:
			print('--> unexpected message is received')
			error = 1
			
	#if(is_WPC_device == 1):
	#	if(pbs_charge_stop_received == 1):
	#		do_it = 0
	#else:
		if(off_response_received == 1):
			do_it = 0
				
		#time.sleep(2)	# wait 2 seconds to see if other commands in between

				
	print_seperation_line()
	#print(' ')
	return error




#***************************************
# detect PRU detect command, wait 5 seconds
# return 0: OK
# return 1: error
#***************************************
def detect_pru_detect_command(detect_address):
	error = 0
	a_response = []
	result = get_a_valid_command(a_response, 7)
	if result == 1:
		print('xxxxx>>> wait too long (', 7, ' seconds ) to detect PRU Detect')
		error = 1
	elif (a_response[2] == DETECT_PRX):
		print('--> DETECT_PRX is received')
		for i in range(0, 6):
			detect_address.append(a_response[3 + i])
	else:
		print('--> unexpected message is received')
		error = 1

	print_seperation_line()
	#print(' ')
	return error


#***************************************
# detect STOP charge command from PRU
# return 0: OK
# return 1: error
#***************************************
def detect_pru_id_command(address, id_number):
	a_response = []
	error = 0
	result = get_a_valid_command(a_response, 5)

	if id_number == 1:
		if result == 1:
			print('xxxxx>>> wait too long (', 5, ' seconds ) to detect PRxID response')
			error = 1
		elif (a_response[2] == ACK_PRXID):
			print('--> PRxID is received')
			for i in range(0, 6):
				if address[i] != (a_response[3 + i]):
					print('xxxxx>>> address not matched')
					error = 1
					break
		else:
			print('--> unexpected message is received')
			error = 1
			
	if id_number == 0:
		if result == 1:
			print('wait (', 5, ' seconds ) and no PRxID response')
		elif (a_response[2] == ACK_PRXID):
			print('--> Error: PRxID is received while ID number is 0')
			error = 1
		else:
			print('--> unexpected message is received')
			error = 1
	
	print_seperation_line()
	#print(' ')
	return error



#***************************************
# detect PRU ID not found
# return 0: OK
# return 1: error
#***************************************
def detect_pru_id_not_found_command():
	a_response = []
	error = 0
	result = get_a_valid_command(a_response, 5)


	if result == 1:
		print('xxxxx>>> wait too long (', 5, ' seconds ) to detect PRxID Not Found response --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
		error = 1
	elif a_response[2] == NOT_FOUND:
		for i in range(0, 5):	# 5 bytes only
			if 0 != a_response[3 + i]:
				print('xxxxx>>> address not matched --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
				error = 1
				break
		if IS_PRX_ID_NOT_FOUND != a_response[8]:
			print('xxxxx>>> ID not found\(0x04\) not matched --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
			error = 1
	else:
		print('--> unexpected message is received --  XXXXXXXXXX  XXXXXXXXXX  XXXXXXXXXX')
		error = 1

	if error == 0:
		print('--> PRxID Not Found is received')
		
	print_seperation_line()
	#print(' ')
	return error
	

#***************************************
#***************************************
def print_test_fail():
	print()
	print(' ---> Below Test Failed !!!  Test Failed !!!  Test Failed !!!')
	#print('----------------------------------------------------------------------------')
	#print()


#***************************************
#***************************************
def print_test_fail_file(fout):
	print('', file=fout)
	print(' ---> Below Test Failed !!!  Test Failed !!!  Test Failed !!!', file=fout)
	#print('----------------------------------------------------------------------------', file=fout)
	#print('', file=fout)


#***************************************
#***************************************
def print_test_success():
	print()
	print(' ---> Below Test Succeeded !!!  Test Succeeded !!!  Test Succeeded !!!')
	#print('----------------------------------------------------------------------------')
	#print()


#***************************************
#***************************************
def print_test_success_file(fout):
	print('', file=fout)
	print(' ---> Below Test Succeeded !!!  Test Succeeded !!!  Test Succeeded !!!', file=fout)
	#print('----------------------------------------------------------------------------', file=fout)
	#print('', file=fout)

	
#***************************************
#***************************************
def summary_report(pru_address, detect_prx_address, is_WPC):
	print()
	
	print('------------------------------ summary report ------------------------------')
	print('FW version  : ', end="")
	for i in range(0, 4):
		print(format(fw_ver[i], '02X'), end="")
		print(' ', end="")
	print()
	
	print('Spec version: ', end="")
	for i in range(0, 2):
		print(format(spec_ver[i], '02X'), end="")
		print(' ', end="")
	print()

	print('PRU address : ', end="")
	for i in range(0, 6):
		print(format(pru_address[i], '02X'), end="")
		print(' ', end="")
	print()

	print('Detect PRx  : ', end="")
	if detect_prx_address == []:
		print('not detected', end="")
	else:
		for i in range(0, 6):
			print(format(detect_prx_address[i], '02X'), end="")
			print(' ', end="")
	print()
	
	print()
	
	print('                                    power  voltage  current  temperature')
	print('PTU readings before charhing	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_start.power, ptu_read_start.voltage, ptu_read_start.current, ptu_read_start.temp))
	#print('PTU readings when charhing  :', ptu_read_on_with_pru.power, ptu_read_on_with_pru.voltage, ptu_read_on_with_pru.current, ptu_read_on_with_pru.temp)
	print('PTU readings when charhing  	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_on_with_pru.power, ptu_read_on_with_pru.voltage, ptu_read_on_with_pru.current, ptu_read_on_with_pru.temp))
	print('PRU readings when charhing  	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(pru_read_on.power, pru_read_on.voltage, pru_read_on.current, pru_read_on.temp))
	print('PTU readings off with PRU   	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_off_with_pru.power, ptu_read_off_with_pru.voltage, ptu_read_off_with_pru.current, ptu_read_off_with_pru.temp))
	print('PTU readings off no PRU	   	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_off_no_pru.power, ptu_read_off_no_pru.voltage, ptu_read_off_no_pru.current, ptu_read_off_no_pru.temp))

	if is_WPC == 1:
		print('     (below readings Under Lock, power should < 5W) ')
		print('lock - PTU readings with PRU	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_lock_with_pru.power, ptu_read_lock_with_pru.voltage, ptu_read_lock_with_pru.current, ptu_read_lock_with_pru.temp))
		print('lock - PRU readings  		:{0:8d} {1:8d} {2:8d} {3:8d}'.format(pru_read_lock.power, pru_read_lock.voltage, pru_read_lock.current, pru_read_lock.temp))
	
		
	#print()
	#print(' ---> Test Pass.  Test Pass.  Test Pass.')
	print('----------------------------------------------------------------------------')
	print()
	print()


#***************************************
#***************************************
def summary_report_file(fout, pru_address, detect_prx_address, is_WPC):
	print(' ', file=fout)
	
	print('------------------------------ summary report ------------------------------', file=fout)

	print('FW version  : ', end="", file=fout)
	for i in range(0, 4):
		print(format(fw_ver[i], '02X'), end="", file=fout)
		
		print(' ', end="", file=fout)
	print(' ', file=fout)
	
	print('Spec version: ', end="", file=fout)
	for i in range(0, 2):
		print(format(spec_ver[i], '02X'), end="", file=fout)
		print(' ', end="", file=fout)
	print(' ', file=fout)

	print('PRU address : ', end="", file=fout)
	for i in range(0, 6):
		print(format(pru_address[i], '02X'), end="", file=fout)
		print(' ', end="", file=fout)
	print(' ', file=fout)

	print('Detect PRx  : ', end="", file=fout)
	if detect_prx_address == []:
		print('not detected', end="", file=fout)
	else:
		for i in range(0, 6):
			print(format(detect_prx_address[i], '02X'), end="", file=fout)
			print(' ', end="", file=fout)
	print('', file=fout)
	
	print('', file=fout)
	
	print('                                    power  voltage  current  temperature', file=fout)
	print('PTU readings before charhing	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_start.power, ptu_read_start.voltage, ptu_read_start.current, ptu_read_start.temp), file=fout)
	#print('PTU readings when charhing  :', ptu_read_on_with_pru.power, ptu_read_on_with_pru.voltage, ptu_read_on_with_pru.current, ptu_read_on_with_pru.temp)
	print('PTU readings when charhing  	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_on_with_pru.power, ptu_read_on_with_pru.voltage, ptu_read_on_with_pru.current, ptu_read_on_with_pru.temp), file=fout)
	print('PRU readings when charhing  	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(pru_read_on.power, pru_read_on.voltage, pru_read_on.current, pru_read_on.temp), file=fout)
	print('PTU readings off with PRU  	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_off_with_pru.power, ptu_read_off_with_pru.voltage, ptu_read_off_with_pru.current, ptu_read_off_with_pru.temp), file=fout)
	print('PTU readings off no PRU	   	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_off_no_pru.power, ptu_read_off_no_pru.voltage, ptu_read_off_no_pru.current, ptu_read_off_no_pru.temp), file=fout)

	if is_WPC == 1:
		print('     (below readings Under Lock, power should < 5W) ', file=fout)
		print('lock - PTU readings with PRU	:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_lock_with_pru.power, ptu_read_lock_with_pru.voltage, ptu_read_lock_with_pru.current, ptu_read_lock_with_pru.temp), file=fout)
		print('lock - PRU readings  		:{0:8d} {1:8d} {2:8d} {3:8d}'.format(pru_read_lock.power, pru_read_lock.voltage, pru_read_lock.current, pru_read_lock.temp), file=fout)
	
	#print('', file=fout)
	#print(' ---> Test Pass.  Test Pass.  Test Pass.', file=fout)
	print('----------------------------------------------------------------------------', file=fout)
	print('', file=fout)
	print('', file=fout)

	
#******************************
# wait user enter a key
#******************************
def wait_user_input():
    return ms_com.getch()


#******************************
# return:
#     	0: user enter 1
#       1: else
#******************************
def ask_exit_prompt():
	a_return = 0
	print('$$$$$>>> Please enter ESC key to exit, other keys to test next unit: ')
	a_char = wait_user_input()
	#print(a_char)
	if a_char == b'\x1b': 	# b'1':
		print('exit test .....')
	else:
		print('test next unit .....')
		a_return = 1
	return a_return



def detect_failure_process(fout):
	print_test_fail()
	print_test_fail_file(fout)
	user_continue = ask_exit_prompt()
	return user_continue


    
#************************************************************************************
def main():
	# Write character 'A' to serial port
	#data = bytearray(b'A')

	# ***** configuration start ***************************************************************
	check_PRX_ID_not_found = 1		# for PRX ID command: 0: need return number; 1: need return PRX ID NOT FOUND
	# ***** configuration  end  ***************************************************************
	
	if(com_port_init()):
		return

	localtime = time.localtime(time.time())
	#print(localtime.tm_year)
	file_name_time_now = 'test_report_' + str(localtime.tm_year) + '_' + str(localtime.tm_mon) + '_' + str(localtime.tm_mday) + '_' + str(localtime.tm_hour) + '_' + str(localtime.tm_min)# + '_' + str(localtime.tm_sec)

	fout = open(file_name_time_now, 'w')

	user_continue = 1
	
	while user_continue == 1:
		error = 0
		
		print('\n\n=============>>> Please power on PBS now ')	# -- to detect Restart and read Versions and PTU readings \n')
		
		print('\n-------- now detect PBS Restart command')
		result = detect_restart_command()
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue
			
		#-------------------------------------------------------
		time.sleep(3) 	# AFA device need to wait 3 seconds *****
		
		print('-------- now test FW and Spec version commands')
		a_err, is_WPC_device = get_version_info(FIRST_TIME_VERSION)
		error += a_err
		
		if(is_WPC_device == 1):
			print('\n#### this is a WPC device test ####\n')
		else:
			print('\n#### this is a AFA device test ####\n')
			
		print('-------- now test PTU reading commands')
		error += get_ptu_readings(ptu_read_start)
		#print('test test test:', ptu_read_start.power, ptu_read_start.voltage, ptu_read_start.current, ptu_read_start.temp )
		#-------------------------------------------------------
		
		# because we need PRU address to read PRU readings, below test is not feasible
		#print('-------- now test PRU reading (power) Not Found commands')
		#error += get_pru_readings_not_found(pru_address, is_WPC_device)


		print('\n\n=============>>> Please put PRU on charge pad')	#-- to test Charge Start and read PTU & PRU readings \n')
		pru_address = []
		detect_prx_address = []
		print('\n-------- now detect PTU and PRU Start Charge commands')
		# for AFA, detect_prx_address may not happen here. How about WPC device ?
		result = detect_start_charge_command_and_pru_addr(pru_address, detect_prx_address)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue

		#-------------------------------------------------------
		time.sleep(2)	# second, wait for readings to get stable

		print('-------- now test FW and Spec version commands')
		a_err = get_version_info(LATER_TIME_VERSION)
		error += a_err
		
		print('\n-------- now test PTU and PRU reading commands')
		error += get_ptu_readings(ptu_read_on_with_pru)


	#if(is_WPC_device == 1):
	#	error += get_pru_readings(detect_prx_address, pru_read_on)
	#else:
		error += get_pru_readings(pru_address, pru_read_on, 0)	#is_WPC_device)
		#-------------------------------------------------------

		print('\n-------- now test Off, On, Lock and Unlock commands, with PRU')
		
		'''	 because some PTU will reply Charge Stop before Ack the command
		error += test_control_commands(ASK_OFF)		# test Off Off Off Off Off Off
		
		result = detect_stop_charge_command(pru_address)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue
		'''
		
		send_command(ASK_OFF)	# see above explaination
		result = detect_off_response_and_stop_charge_command(pru_address)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue

		print('-------- now test FW and Spec version commands')
		a_err = get_version_info(LATER_TIME_VERSION)
		error += a_err

		print('-------- now test PTU reading commands')
		error += get_ptu_readings(ptu_read_off_with_pru)

		print('-------- now test PRU reading (power) Not Found commands')
		error += get_pru_readings_not_found(pru_address, 0)	#is_WPC_device)

		if check_PRX_ID_not_found == 0:
			print('\n-------- 111 now test 0 PRx ID command. PTU Off, with PRU')
			error += test_pru_id_command(ZERO_PRU_ID)
			result = detect_pru_id_command(pru_address, ZERO_PRU_ID)	# 0
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue
		else:
			print('\n-------- 111 now test PRx ID Not Found command. PTU Off, with PRU')
			send_command(ASK_PRU_ID)	#error += test_pru_id_command(ZERO_PRU_ID)
			result = detect_pru_id_not_found_command()	# Not Found
			error += result
			'''
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue'''
		

		print('\n-------- now test On command, with PRU')
		error += test_control_commands(ASK_ON)		# test On On On On On On On On
		pru_address = []
		detect_prx_address = []
		# for AFA, detect_prx_address may not happen here. How about WPC device ?
		result = detect_start_charge_command_and_pru_addr(pru_address, detect_prx_address)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue

		if(is_WPC_device == 1):	# for WPC
		
			print('\n-------- now test Lock command for WPC. Charge is possible.')
			
			error += test_control_commands(ASK_LOCK)	# test Lock Lock Lock Lock Lock

			# WPC can charge when Locked. Power should be < 5W.
			print('\n-------- now test PTU and PRU reading commands when Lock. Should < 5W')
			error += get_ptu_readings(ptu_read_lock_with_pru)
			error += get_pru_readings(pru_address, pru_read_lock, 0)	#is_WPC_device)
			

			print('\n-------- now test Unlock command')
			error += test_control_commands(ASK_UNLOCK)		# test UnLock UnLock UnLock UnLock

				
		else:	# for AFA
		
			#'''
			print('\n-------- now test Lock command for AFA. Charge is Not possible.')
			error += test_control_commands(ASK_LOCK)	# test Lock Lock Lock Lock Lock
			result = detect_stop_charge_command(pru_address)
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue

			# AFA can detect PRU when Locked, but no charge
			detect_prx_address_AFA_lock = []
			result = detect_pru_detect_command(detect_prx_address_AFA_lock)
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue

			print('\n-------- now test Unlock command')
			error += test_control_commands(ASK_UNLOCK)		# test UnLock UnLock UnLock UnLock
			pru_address = []
			detect_prx_address = []
			# for AFA, detect_prx_address may not happen here. How about WPC device ?
			result = detect_start_charge_command_and_pru_addr(pru_address, detect_prx_address)
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue
			#'''
			
		
		print('\n-------- 222 now test 1 PRx ID command. PTU ON, with PRU')
		error += test_pru_id_command(ONE_PRU_ID)
		result = detect_pru_id_command(pru_address, ONE_PRU_ID)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue

		print('\n-------- now test PTU Power command every 20 ms for 10 times')
		time.sleep(1) # 1 s
		for i in range(0, 10):
			return_data = []
			result = command_tx_rx(0x09, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU power')
			if result == 0:	# OK
				#reading.power = return_data[0] * 256 + return_data[1]
				print('PTU Power reading :{0:8d} '.format(return_data[0] * 256 + return_data[1]))
			else:
				error += 1
			time.sleep(0.02) # 20ms

		print('\n-------- now test PTU Power and Voltage command continuously for 5 times')
		time.sleep(1) # 1 s
		for i in range(0, 5):
			return_data = []
			result = command_tx_rx(0x09, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU power')
			if result == 0:	# OK
				#reading.power = return_data[0] * 256 + return_data[1]
				print('PTU Power reading :{0:8d} '.format(return_data[0] * 256 + return_data[1]))
			else:
				error += 1

			return_data = []
			result = command_tx_rx(0x0A, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'PTU voltage')
			if result == 0:	# OK
				#reading.power = return_data[0] * 256 + return_data[1]
				print('PTU Voltage reading :{0:8d} '.format(return_data[0] * 256 + return_data[1]))
			else:
				error += 1

			
		print('\n\n=============>>> Please remove PRU from charge pad. PTU is ON now')	#-- to test Charge Stop and Not Found responses \n')
		
		print('\n-------- now detect PTU and PRU Stop Charge commands')
		result = detect_stop_charge_command(pru_address)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue
			
		print('-------- now test PRU reading (power) Not Found commands')
	#if(is_WPC_device == 1):
	#	error += get_pru_readings_not_found(detect_prx_address)
	#else:
		error += get_pru_readings_not_found(pru_address, 0)	#is_WPC_device)

		# PTU is ON, so need to reply 0 PRU number and no more ID number reply
		print('\n-------- 333 now test 0 PRx ID command. PTU ON, no PRU')
		error += test_pru_id_command(ZERO_PRU_ID)
		result = detect_pru_id_command(pru_address, ZERO_PRU_ID)	# 0
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue
		#-------------------------------------------------------

		
		#-------------------------------------------------------
		if(is_WPC_device == 1):
			print('\n-------- now test PTU Off command')
		else:
			print('\n-------- now test PTU Off command')
			#print('\n-------- now test Off, On, Lock and Unlock commands')
		
		'''	 because some PTU replies Charge Stop before Ack the command
		error += test_control_commands(ASK_OFF)		# test Off Off Off Off Off Off
		
		result = detect_stop_charge_command(pru_address)
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue
		'''
		
		send_command(ASK_OFF)
		result = detect_off_response()
		if result == 1:
			user_continue = detect_failure_process(fout)
			continue

		print('-------- now test FW and Spec version commands')
		a_err = get_version_info(LATER_TIME_VERSION)
		error += a_err

		print('-------- now test PTU reading commands')
		error += get_ptu_readings(ptu_read_off_no_pru)

		print('-------- now test PRU reading (power) Not Found commands')
		error += get_pru_readings_not_found(pru_address, 0)	#is_WPC_device)

		if check_PRX_ID_not_found == 0:
			print('\n-------- 444 now test 0 PRx ID command. PTU OFF, no PRU')
			error += test_pru_id_command(ZERO_PRU_ID)
			result = detect_pru_id_command(pru_address, ZERO_PRU_ID)	# 0
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue
		else:
			print('\n-------- 444 now test PRx ID Not Found command. PTU OFF, no PRU')
			send_command(ASK_PRU_ID)	#error += test_pru_id_command(ZERO_PRU_ID)
			result = detect_pru_id_not_found_command()	# Not Found
			error += result
			'''
			if result == 1:
				user_continue = detect_failure_process(fout)
				continue'''

		print('\n\n=============>>> Please put PRU on charge pad again ASAP when PTU is Off')	#-- to test no response when PTU off
		a_response = []
		result = get_a_valid_command(a_response, 5)

		if result == 1:
			print('wait (',5, 'seconds ) and no response is received')
		else:
			print('--> unexpected message is received')
			error += 1

		if error > 0:	# any error happen
			print_test_fail()
			print_test_fail_file(fout)
		else:
			print_test_success()
			print_test_success_file(fout)

		
		if(is_WPC_device == 1):
			summary_report(pru_address, detect_prx_address, is_WPC_device)
			summary_report_file(fout, pru_address, detect_prx_address, is_WPC_device)
		else:
			# for AFA, detect_prx_address may not happen. But detect_prx_address_AFA_lock is always available
			summary_report(pru_address, detect_prx_address_AFA_lock, is_WPC_device)
			summary_report_file(fout, pru_address, detect_prx_address_AFA_lock, is_WPC_device)

		user_continue = ask_exit_prompt()

	ComPort.close()
	fout.close()
#************************************************************************************


if __name__ == "__main__":
    main()













'''
# coding=UTF-8
import time
import serial

ptn = [0xAA,0x50,0x60,0x70] 

def main():
    
    ser = serial.Serial('COM8', 115200, timeout=0.5)
    ary = bytearray(ptn)
    ser.write(ary)
    time.sleep(0.1)
    ser.close()    

if __name__ == "__main__":
    main()
'''





'''
import serial
ser = serial.Serial(8)  # open first serial port
print (ser.portstr)       # check which port was really used
ser.write("hello")      # write a string
ser.close()             # close port
'''



'''
import serial, time
#initialization and open the port

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

ser = serial.Serial()
#ser.port = "/dev/ttyUSB0"
ser.port = "/dev/ttyUSB7"
#ser.port = "/dev/ttyS2"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write

try: 
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()

if ser.isOpen():

    try:
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output 
                 #and discard all that is in buffer

        #write data
        ser.write("AT+CSQ")
        print("write data: AT+CSQ")

       time.sleep(0.5)  #give the serial port sometime to receive the data

       numOfLines = 0

       while True:
          response = ser.readline()
          print("read data: " + response)

        numOfLines = numOfLines + 1

        if (numOfLines >= 5):
            break

        ser.close()
    except Exception, e1:
        print "error communicating...: " + str(e1)

else:
    print "cannot open serial port "
'''







'''
import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    #port='/dev/ttyUSB1',
    port='COM8'
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

ser.isOpen()

print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

input=1
while 1 :
    # get keyboard input
    input = raw_input(">> ")
        # Python 3 users
        # input = input(">> ")
    if input == 'exit':
        ser.close()
        exit()
    else:
        # send the character to the device
        # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
        ser.write(input + '\r\n')
        out = ''
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(1)
        while ser.inWaiting() > 0:
            out += ser.read(1)

        if out != '':
            print ">>" + out
'''
