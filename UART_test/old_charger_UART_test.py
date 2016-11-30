
import time
import serial           # import the module

ComPort = serial.Serial('COM8') # open COM8
ComPort.baudrate = 115200 # set Baud rate to 115200
ComPort.bytesize = 8    # Number of data bits = 8
ComPort.parity   = 'N'  # No parity
ComPort.stopbits = 1    # Number of Stop bits = 1

def command_tx_rx(cmd_tx, data_byte, cmd_name):
	tx_list = []
	checksum = 0
	tx_list.append(0xA5)
	tx_list.append(0xA5)
	tx_list.append(cmd_tx)
	for i in range(0, 6):
		tx_list.append(data_byte[i])
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

	rx_list = []
	checksum = 0
	#data = ComPort.readline()        	# Wait and read data, need 0D 0A
	for i in range(0, 10):				# read 10 bytes
		data = ComPort.read()        	# Wait and read data, one byte
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
		print('-->', cmd_name, 'Response is correct')
	else:
		print('-->', cmd_name, 'Response is wrong')

	print('==============================')
	print(' ')
	return 0


#************************************************************************************
def main():
	# Write character 'A' to serial port
	#data = bytearray(b'A')

	# ask FW version
	#data = bytearray([0xA5, 0xA5, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x51])
	#No = ComPort.write(data)

	wait_time = 0

	command_tx_rx(0x07, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'FW Ver')
	time.sleep(wait_time)

	command_tx_rx(0x08, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'Spec Ver')
	time.sleep(wait_time)

	command_tx_rx(0x09, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU power')
	time.sleep(wait_time)

	command_tx_rx(0x0A, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU voltage')
	time.sleep(wait_time)

	command_tx_rx(0x0B, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU current')
	time.sleep(wait_time)

	command_tx_rx(0x0C, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 'PTU temperature')
	time.sleep(wait_time)

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
