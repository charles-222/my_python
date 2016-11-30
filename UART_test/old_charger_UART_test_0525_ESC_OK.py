
# todo:  read COM port from command line

import time
import serial           # import the module
import msvcrt as m

READ_SERIAL_TIMEOUT 	= 5  	# 3 seconds
COMMAND_TIME_OUT_TIME 	= 10		# 10 second

ComPort = serial.Serial('COM8') # open COM8
ComPort.baudrate 	= 115200 	# set Baud rate to 115200
ComPort.bytesize 	= 8    		# Number of data bits = 8
ComPort.parity   	= 'N'  		# No parity
ComPort.stopbits 	= 1    		# Number of Stop bits = 1
ComPort.timeout		= READ_SERIAL_TIMEOUT		# 0.5 second timeout for read(), see http://pyserial.readthedocs.io/en/latest/pyserial_api.html

# PTU vs PRU
IS_PTU				= 0x00
IS_PRU				= 0x01

# for not found response
IS_POWER			= 0x00
IS_VOLTAGE			= 0x01
IS_CURRENT			= 0x02
IS_TEMPERATURE		= 0x03

# for PBS start/stop charge
START_CHARGE		= 0x00
STOP_CHARGE			= 0x01

# for command's Opcode
ASK_POWER			= 0x09
ASK_VOLTAGE			= 0x0A
ASK_CURRENT			= 0x0B
ASK_TEMPERATURE		= 0x0C

ACK_PRXID			= 0x8E
NOT_FOUND			= 0x8F

DETECT_PRX     		= 0x90
PBS_CHARGE     		= 0x91
PRU_CHARGE_START 	= 0x92
PRU_CHARGE_STOP 	= 0x93
FAULT_AUTO		 	= 0x94
PBS_RESTART_AUTO	= 0x95

class PXU_Readings:
	power = -1
	voltage = -1
	current = -1
	temp = -127

fw_ver 				= []
spec_ver			= []
pru_address 		= []
detect_prx_address  = []

ptu_read_start 				= PXU_Readings()
ptu_read_with_pru_on 		= PXU_Readings()
#ptu_read_after_pru_removal 	= PXU_Readings()

pru_read_on_pad 			= PXU_Readings()
#pru_read_after_removal 		= PXU_Readings()



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
	for i in range(0, 6):
		tx_list.append(tx_data[i])
	for i in range(0, 9):
		checksum += tx_list[i]
	checksum %= 256
	tx_list.append(checksum)
	No = ComPort.write(bytearray(tx_list))
	#'''
	print(cmd_name, 'Command sent:     ', end="")
	#print(tx_list[0:10])
	for i in range(0, 10):
		print(format(tx_list[i], '02X'), end="")
		print(' ', end="")
	print()
	#'''

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
				print('-->', cmd_name, 'Response is wrong')
				return_value = 1
		elif pxu == IS_PRU:
			if rx_list[8] == 0x01:
				print('-->', cmd_name, 'Response is correct')
			else:
				print('-->', cmd_name, 'Response is wrong')
				return_value = 1
		else:
			print('-->', cmd_name, 'Response is wrong')
			return_value = 1
	else:
		print('-->', cmd_name, 'Response is wrong')
		return_value = 1

	print('==============================')
	print(' ')

	for i in range(0, 6):
		return_data.append(rx_list[i + 3])
	
	return return_value



#*******************************************************
# send query command and expect to get "not found" response
# wait up to READ_SERIAL_TIMEOUT * 10 = 10 seconds
# tx_data: payload to be sent
# type: IS_POWER, IS_VOLTAGE, IS_CURRENT, IS_TEMPERATURE
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
	#'''
	print(cmd_name, 'Command sent:     ', end="")
	#print(tx_list[0:10])
	for i in range(0, 10):
		print(format(tx_list[i], '02X'), end="")
		print(' ', end="")
	print()
	#'''

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
		print('-->', cmd_name, 'Response Not found is correct')
	else:
		print('-->', cmd_name, 'Response Not found is wrong')
		return_value = 1

	print('==============================')
	print(' ')
	
	return return_value


#*********************************************
# return the valid command received
# return_command is passed in as an empty list ([])
# return:
#		0: OK
#		1: timeout or fail
#*********************************************
def get_a_valid_command(return_command):
	response_found = 0
	response_length = 0
	response_list = []

	timeout = time.time() + COMMAND_TIME_OUT_TIME
	
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
			
	for i in range(0, 10):	
		return_command.append(response_list[i])
		
	print('valid Command found: ', end="")
	for i in range(0, 10):
		print(format(response_list[i], '02X'), end="")
		print(' ', end="")

	print()
	#print('==============================')
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
		result = get_a_valid_command(a_response)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to get PBS Restart message')
			return 1	
			
		if(a_response[2] == PBS_RESTART_AUTO):
			pbs_restart_received = 1
			print('-->PBS_RESTART is received, PBS restarts')

	print('==============================')
	print(' ')
	return 0

#*********************************************
# Version information
# return:
#		0: OK
#		1: error
#*********************************************
def get_version_info():
	wait_time = 0	# second
	return_data = []
	error = 0
	result = command_tx_rx(0x07, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'FW Ver')
	if result == 0:	# OK
		for i in range(0, 4):
			fw_ver.append(return_data[i + 1])
	else:
		error = 1
	time.sleep(wait_time)

	return_data = []
	result = command_tx_rx(0x08, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], IS_PTU, return_data, 'Spec Ver')
	if result == 0:	# OK
		for i in range(0, 2):
			spec_ver.append(return_data[i + 4])
	else:
		error = 1

	return error

	
#*********************************************
# PTU   PTU   PTU
# return:
#		0: OK
#		1: error
#*********************************************
def get_ptu_readings(reading):
	wait_time = 0	# second
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

	return error

#********************************
# PRU   PRU   PRU
# return:
#		0: OK
#		1: error
#********************************
def get_pru_readings(address, reading):
	wait_time = 0	# second
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

	return error


#********************************
# PRU   PRU   PRU
# readings not found
# return:
#		0: OK
#		1: error
#********************************
def get_pru_readings_not_found(address):
	wait_time = 0	# second
	data = []
	error = 0
	for i in range(0, 5):
		data.append(address[i + 1])
	data.append(IS_PRU)
	
	result = command_tx_rx_not_found(0x09, data, IS_POWER, 'PRU power')
	if result == 1:	# Fail
		error = 1
	time.sleep(wait_time)

	result = command_tx_rx_not_found(0x0A, data, IS_VOLTAGE, 'PRU voltage')
	if result == 1:	# Fail
		error = 1
	time.sleep(wait_time)

	result = command_tx_rx_not_found(0x0B, data, IS_CURRENT, 'PRU current')
	if result == 1:	# Fail
		error = 1
	time.sleep(wait_time)

	result = command_tx_rx_not_found(0x0C, data, IS_TEMPERATURE, 'PRU temperature')
	if result == 1:	# Fail
		error = 1

	return error


#****************************************************************************
# detect START charge command from PRU, maybe can detect Detect PRx here too
# return 
#		0: OK
# 		1: error
#****************************************************************************
def detect_charge_command_and_pru_addr(address, detect_address):
	pbs_charge_start_received = 0
	pru_charge_start_received = 0
	while(pbs_charge_start_received != 1 or pru_charge_start_received != 1):
		a_response = []
		result = get_a_valid_command(a_response)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to detect PRU on pad')
			return 1
			
		if(a_response[2] == PBS_CHARGE and a_response[8] == START_CHARGE):
			pbs_charge_start_received = 1
			print('-->PBS_CHARGE is received, PBS is charging PRU')
		elif(a_response[2] == PRU_CHARGE_START):
			pru_charge_start_received = 1
			print('--PRU_CHARGE_START is received, PRU is under charging')
			for i in range(0, 6):
				address.append(a_response[3 + i])
		elif(a_response[2] == DETECT_PRX):
			print('--DETECT_PRX is received')
			timeout = time.time()	# no need to wait anymore
			for i in range(0, 6):
				detect_address.append(a_response[3 + i])
		else:
			print('-->unexpected message is received')

		time.sleep(2)	# wait 2 seconds to see if other commands in between
				
	print('==============================')
	print(' ')
	return 0


#***************************************
# detect STOP charge command from PRU
# return 0: OK
# return 1: error
#***************************************
def detect_stop_charge_command(address):
	pbs_charge_stop_received = 0
	pru_charge_stop_received = 0
	
	while(pbs_charge_stop_received != 1 or pru_charge_stop_received != 1):
		a_response = []
		result = get_a_valid_command(a_response)
		if result == 1:
			print('xxxxx>>> wait too long (', COMMAND_TIME_OUT_TIME, ' seconds ) to detect PRU removal')
			return 1
			
		if(a_response[2] == PBS_CHARGE and a_response[8] == STOP_CHARGE):
			pbs_charge_stop_received = 1
			print('-->PBS_CHARGE is received, PBS stops charging PRU')
		if(a_response[2] == PRU_CHARGE_STOP):
			for i in range(0, 6):	# compare PRU address
				if(address[i] != a_response[i + 3]):
					return 1		
			pru_charge_stop_received = 1
			print('--PRU_CHARGE_STOP is received, PRU is not under charging')

	print('==============================')
	print(' ')
	return 0

	
#***************************************
#***************************************
def print_test_fail():
	print()
	print(' ---> Test Fail !!!  Test Fail !!!  Test Fail !!!')
	print()


#***************************************
#***************************************
def summary_report():
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
	
	print('                                power  voltage  current  temperature')
	print('PTU readings before charhing:{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_start.power, ptu_read_start.voltage, ptu_read_start.current, ptu_read_start.temp))
	#print('PTU readings when charhing  :', ptu_read_with_pru_on.power, ptu_read_with_pru_on.voltage, ptu_read_with_pru_on.current, ptu_read_with_pru_on.temp)
	print('PTU readings when charhing  :{0:8d} {1:8d} {2:8d} {3:8d}'.format(ptu_read_with_pru_on.power, ptu_read_with_pru_on.voltage, ptu_read_with_pru_on.current, ptu_read_with_pru_on.temp))
	print('PRU readings when charhing  :{0:8d} {1:8d} {2:8d} {3:8d}'.format(pru_read_on_pad.power, pru_read_on_pad.voltage, pru_read_on_pad.current, pru_read_on_pad.temp))
	print()
	print(' ---> Test Pass.  Test Pass.  Test Pass.')
	print('----------------------------------------------------------------------------')
	print()


#******************************
# wait user enter a key
#******************************
def wait_user_input():
    return m.getch()


#******************************
# return:
#     	0: user enter 1
#       1: else
#******************************
def ask_exit_prompt():
	a_return = 0
	print('==========>>> Please enter ESC key to exit, other keys to test next unit: ')
	a_char = wait_user_input()
	#print(a_char)
	if a_char == b'\x1b': 	# b'1':
		print('exit test .....')
	else:
		print('test next unit .....')
		a_return = 1
	return a_return

    
#************************************************************************************
def main():
	# Write character 'A' to serial port
	#data = bytearray(b'A')

	user_continue = 1
	
	while user_continue == 1:
		error = 0
		print()
		
		print('==========>>> Please power on PBS now ')
		#'''
		result = detect_restart_command()
		if result == 1:
			print_test_fail()
			#ComPort.close()
			user_continue = ask_exit_prompt()
			continue #return
		#'''
		#-------------------------------------------------------
		error += get_version_info()
		error += get_ptu_readings(ptu_read_start)
		#print('test test test:', ptu_read_start.power, ptu_read_start.voltage, ptu_read_start.current, ptu_read_start.temp )
		#-------------------------------------------------------

		print('==========>>> Please put PRU on charge pad ')
		result = detect_charge_command_and_pru_addr(pru_address, detect_prx_address)
		if result == 1:
			print_test_fail()
			#ComPort.close()
			user_continue = ask_exit_prompt()
			continue #return

		#-------------------------------------------------------
		time.sleep(2)	# second, wait for readings to get stable
		error += get_ptu_readings(ptu_read_with_pru_on)
		error += get_pru_readings(pru_address, pru_read_on_pad)
		#-------------------------------------------------------

		print('==========>>> Please remove PRU from charge pad ')
		result = detect_stop_charge_command(pru_address)
		if result == 1:
			print_test_fail()
			#ComPort.close()
			user_continue = ask_exit_prompt()
			continue #return
			
		error += get_pru_readings_not_found(pru_address)

		if error > 0:	# any error happen
			print_test_fail()
		else:
			summary_report()

		user_continue = ask_exit_prompt()

	ComPort.close()

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
