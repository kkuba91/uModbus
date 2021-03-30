#!/usr/bin/env python3

import socket
import math
import time

"""  
    Modbus client/master  
    TCP prepared, RTU in further perspective
    """

## Description:
help = "\nExample of use as Master:\n" \
       "mb1 = uModBus()\n" \
       "mb1.TCP_Init(ip='127.0.0.1', id=23, master=True)  # test on local\n" \
       "\n" \
       "Now build a request - Function 3 - Read 6 Holding Registers starting with address 0:\n" \
       "mb1.TCP_requestSend(UnitID=25, Function=3, Offset=0, Quantity=6, ForceData=None)\n" \
       "Parse an answer:\n" \
       "mb1.TCP_responseRead()\n" \
       "Now if communication works, data of right registers should be parsed into mb1 object\n" \
       "\n" \
       "Example of use as Slave:\n" \
       "mb2 = uModBus()\n" \
       "mb2.TCP_Init(ip='127.0.0.1', id=22, master=False)  # test on local\n" \
       "Now Read-Response methods (in loop):\n" \
       "while True:\n" \
       "    mb2.TCP_requestRead()\n" \
       "    mb2.TCP_responseSend()\n" \
       "\n" \
       "\n\n"


## Main Class for modbus object
class uModBus:
    __DEBUG = False     # MACRO activate debug print of packets inside some function

    ## Simple structure for data remembrance of request for master object
    class Requested:
        Id = 0
        Offset = 0
        Quantity = 0

    """   Micro Modbus Object for Frame constructor   """
    def __init__(self):
        # Some typical data definition for modbus device
        self.UnitID = 2
        self.Inputs = [
            False, False, False, False, False, False, False, False, False, False, 
            False, False, False, False, False, False, False, False, False, False]
        self.Outputs = [
            False, False, False, False, False, False, False, False, False, False, 
            False, False, False, False, False, False, False, False, False, False]
        self.Registers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.InputRegisters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.TCP = None
        self.TCP_IP = "127.0.0.1"
        self.TCP_PORT = 502
        self.TCP_msg = []
        self.RTU_msg = []
        self.TCP_delay = 300
        self.RTU_delay = 300
        self.__TCP_tx = 0
        self.__TCP_length = 0
        self.__TCP_clientConnected = None
        self.__TCP_clientAddress = None
        self.__TCP_connected = False
        self.__RAW_request = None
        self.__requested = self.Requested()

    # Init of TCP socket for further connections:
    def TCP_Init(self, ip, id, master):
        self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_IP = ip
        self.UnitID = id
        if master == False:
            self.__TCP_InitSlave()
        else:
            self.__TCP_InitMaster()
        return self

    ## Private
    # Socket preapre for Master function:
    def __TCP_InitMaster(self):
        try:
            self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.TCP.connect((self.TCP_IP, self.TCP_PORT))
            self.__TCP_connected = True
        except BaseException as e:
            print(e)
            self.__TCP_connected = False

    ## Private
    # Socket preapre for Slave function:
    def __TCP_InitSlave(self):
        self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP.bind((self.TCP_IP, self.TCP_PORT))
        self.TCP.listen()

    # Read external request (Slave function):
    def TCP_requestRead(self):
        try:
            if self.__TCP_connected == False:
                (self.__TCP_clientConnected, self.__TCP_clientAddress) = self.TCP.accept()
            d = self.__TCP_clientConnected.recv(1024)
            if d:
                dataFromMaster = list(bytes(d))
                self.__TCP_connected = True
                tx1 = dataFromMaster.pop(0)
                tx2 = dataFromMaster.pop(0)
                self.__TCP_tx = int.from_bytes([tx1, tx2], byteorder='big', signed=False)
                dataFromMaster.pop(0)
                dataFromMaster.pop(0)
                l1 = dataFromMaster.pop(0)
                l2 = dataFromMaster.pop(0)
                self.__TCP_length = int.from_bytes([l1, l2], byteorder='big', signed=False)
                self.__RAW_request = dataFromMaster
            else:
                self.__TCP_connected = False
        except BaseException as e:
            print("TCP_requestRead: ", e)
            self.__TCP_connected = False

    # Respond to external device (Slave function):
    def TCP_responseSend(self):
        try:
            if self.__TCP_connected == True:
                self.TCP_msg.clear()
                dataToServer = self.__requestRead(self.__RAW_request, False)
                dataToServer.pop()
                dataToServer.pop()
                self.__TCP_length = len(dataToServer)
                self.TCP_msg.extend(self.__TCP_tx.to_bytes(2, byteorder='big'))
                self.TCP_msg.extend([0x00, 0x00])
                self.TCP_msg.extend(self.__TCP_length.to_bytes(2, byteorder='big'))
                self.TCP_msg.extend(dataToServer)
                self.__TCP_clientConnected.send(bytearray(self.TCP_msg))
                if self.__DEBUG:
                    print("All packets sent:\n", self.TCP_msg)
            return 0
        except BaseException as e:
            print("TCP_responseSend: ", e)
            self.__TCP_connected = False
            return -1

    # Send request to a device (Master function):
    def TCP_requestSend(self, UnitID, Function, Offset, Quantity, ForceData):
        self.__TCP_requestBuild(UnitID=UnitID, Function=Function, Offset=Offset, Quantity=Quantity, ForceData=ForceData)
        self.__requested.Id = UnitID
        self.__requested.Offset = Offset
        self.__requested.Quantity = Quantity
        try:
            if self.__TCP_connected == False:
                self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.TCP.connect((self.TCP_IP, self.TCP_PORT))
            self.TCP.send(bytearray(self.TCP_msg))
            # print("Sent request: ", list(self.TCP_msg))
            self.__TCP_connected = True
        except BaseException as e:
            print("TCP_requestSend: ", e)
    
    def __bitInByte(self, B, nr):
        return (B&(2**nr) != 0)

    # Private
    # Parsing data from response message:
    def __responseRead(self, data, checkCRC):
        quantity = 0
        IDok = (data[0] == self.__requested.Id)
        crcOK = True
        if checkCRC:
            crcOK = self.check_crc(data)
        if IDok and crcOK:
            if data[1] == 0x01:
                for i in range(self.__requested.Quantity):
                    self.Outputs[self.__requested.Offset+i] = self.__bitInByte( data[3+int(i/8)], i % 8 )
                return False
            if data[1] == 0x02:
                for i in range(self.__requested.Quantity):
                    self.Inputs[self.__requested.Offset+i] = self.__bitInByte( data[3+int(i/8)], i % 8 )
                return False
            if data[1] == 0x03:
                quantity = data[2]
                for addr in range(int(quantity/2)):
                    self.Registers[addr+self.__requested.Offset] = int.from_bytes(
                        [data[3+(2*addr)], data[4+(2*addr)]],
                        byteorder='big',
                        signed=False)
                return False
            if data[1] == 0x04:
                quantity = data[2]
                for addr in range(int(quantity/2)):
                    self.InputRegisters[addr+self.__requested.Offset] = int.from_bytes(
                        [data[3+(2*addr)], data[4+(2*addr)]],
                        byteorder='big',
                        signed=False)
                return False
            if data[1] == 0x05:
                val = data[4]
                if val == 0xFF:
                    self.Outputs[self.__requested.Offset] = True
                else:
                    self.Outputs[self.__requested.Offset] = False
                return False
            if data[1] == 0x06:
                self.Registers[self.__requested.Offset] = int.from_bytes(
                    [data[4], data[5]],
                    byteorder='big',
                    signed=False)
                return False
        else:
            return True

    # Parse a respond from a device (Master function):
    def TCP_responseRead(self):
        msg = None
        try:
            if self.__TCP_connected == True:
                resp = self.TCP.recv(1024)
                while not resp:
                    resp = self.TCP.recv(1024)
                msg = list(resp)
                msg.pop(0)
                msg.pop(0)
                msg.pop(0)
                msg.pop(0)
                msg.pop(0)
                msg.pop(0)
                self.TCP.close()
                self.__TCP_connected = False
                if self.__DEBUG:
                    print("Response read: ", list(bytes(msg)))
                self.__responseRead(data=list(bytes(msg)), checkCRC=False)
                time.sleep(self.TCP_delay/1000)
                return list(bytes(msg))
        except BaseException as e:
            print("TCP_responseRead: ", e)
            self.__TCP_connected = False
            return list(bytes([0x00]))

    # Private
    # Generate Modbus CRC (for RTU):
    def __calc_crc(self, data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if ((crc & 1) != 0):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    # Check of packet ending CRC (Modbus CRC validation for RTU):
    def check_crc(self, data):
        tempCRC = [0, 0]
        tempCRC[0] = data.pop()
        tempCRC[1] = data.pop()
        data = self.__crcMB(data)
        if tempCRC[0] == data.pop() and tempCRC[1] == data.pop():
            return True
        else:
            return False

    # Private
    # Help function for CRC extension:
    def __crcMB(self, data):
        bb = self.__calc_crc(data).to_bytes(2, byteorder="little")
        data.extend(bb)
        return data

    # Private
    # Prepare request packet:
    def __RTU_requestBuild(self, UnitID, Function, Offset, Quantity, ForceData):
        self.RTU_msg.clear()
        self.RTU_msg = [UnitID, Function]
        tempBytes = Offset.to_bytes(2, byteorder='big', signed=False)
        self.RTU_msg.extend([tempBytes[0], tempBytes[1]])
        tempBytes = Quantity.to_bytes(2, byteorder='big', signed=False)
        self.RTU_msg.extend([tempBytes[0], tempBytes[1]])
        if Function == 15:
            q = int((Quantity-1)/8+1)
            self.RTU_msg.extend([q])
            self.RTU_msg.extend(ForceData)
        if Function == 16:
            q = Quantity*2
            self.RTU_msg.extend([q])
            self.RTU_msg.extend(ForceData)
        self.RTU_msg = list(self.__crcMB(self.RTU_msg))
        return self.RTU_msg

    # Debug - public function for request packet in RTU:
    def debug_RTU_requestBuild(self, UnitID, Function, Offset, Quantity, ForceData):
        return self.__RTU_requestBuild(UnitID=UnitID, Function=Function, Offset=Offset, Quantity=Quantity, ForceData=ForceData)
    
    # Debug - public function for request packet in TCP:
    def debug_TCP_requestBuild(self, UnitID, Function, Offset, Quantity, ForceData):
        return self.__TCP_requestBuild(UnitID=UnitID, Function=Function, Offset=Offset, Quantity=Quantity, ForceData=ForceData)
    
    # Private
    # Building the request packet, ForceData is optional for Write functions:
    def __TCP_requestBuild(self, UnitID, Function, Offset, Quantity, ForceData):
        self.TCP_msg.clear()
        self.__TCP_tx = self.__TCP_tx + 1
        if self.__TCP_tx >= 65535:
            self.__TCP_tx = 0
        self.TCP_msg.extend(self.__TCP_tx.to_bytes(2, byteorder='big'))
        self.TCP_msg.extend([0x00, 0x00])

        data = []
        data = [UnitID, Function]
        tempBytes = Offset.to_bytes(2, byteorder='big', signed=False)
        data.extend([tempBytes[0], tempBytes[1]])
        if Function == 1 or Function == 2 or Function == 3 or Function == 4:
            tempBytes = Quantity.to_bytes(2, byteorder='big', signed=False)
            data.extend([tempBytes[0], tempBytes[1]])
        if Function == 5:
            if ForceData == None or ForceData == False or ForceData == 0:
                data.extend([0x00, 0x00])
            else:
                data.extend([0xFF, 0x00])
        if Function == 6:
            if ForceData == None or ForceData == False:
                data.extend([0x00, 0x00])
            else:
                try:
                    tempBytes = ForceData.to_bytes(2, byteorder='big', signed=False)
                except BaseException as e:
                    tempBytes = (1).to_bytes(2, byteorder='big', signed=False)
                    print("RequestBuild-Function 6: ", e)
                data.extend(tempBytes)
        if Function == 15:
            q = int((Quantity-1)/8+1)
            data.extend([q])
            data.extend(ForceData)
        if Function == 16:
            q = Quantity*2
            data.extend([q])
            data.extend(ForceData)

        self.__TCP_length = len(data)
        self.TCP_msg.extend(self.__TCP_length.to_bytes(2, byteorder='big'))
        try:
            self.TCP_msg.extend(data)
        except BaseException as e:
            print("RequestBuild: ", e)
        return list(self.TCP_msg)
    
    # Debug - public function for request print in hex data (TCP):
    def debug_TCP_msgPrint(self):
        print('[{}]'.format(', '.join(hex(x) for x in self.TCP_msg)) )
        pass

    # Debug - public function for request print in hex data (RTU):
    def debug_RTU_msgPrint(self):
        print('[{}]'.format(', '.join(hex(x) for x in self.RTU_msg)) )
        pass

    # Private
    # Read ModbusTCP message without prefix
    # Returning answer message
    def __requestRead(self, data, checkCRC):
        okToRead = False
        quantity = 0
        offset = 0
        value = 0
        IDok = (data[0] == self.UnitID)
        if checkCRC:
            okToRead = self.check_crc(data)
        else:
            okToRead = True
        if okToRead and IDok:
            if data[1] == 0x01:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.__ReadOutput(offset-1, quantity)
            if data[1] == 0x02:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.__ReadInput(offset-1, quantity)
            if data[1] == 0x03:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.__ReadRegisters(offset-1, quantity)
            if data[1] == 0x04:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.__ReadIRegisters(offset-1, quantity)
            if data[1] == 0x05:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                if data[4] == 0xFF and data[5] == 0x00:
                    value = True
                if data[4] == 0x00 and data[5] == 0x00:
                    value = False
                if data[5] == 0x00 and (data[4] == 0xFF or data[4] == 0x00):
                    return self.__WriteCoil(offset-1, value)
                else:
                    return -1
            if data[1] == 0x06:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                val = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.__WriteRegister(offset-1, val)
        else:
            return -1

    # Private
    # Function 1 (list of bits with some offset and range)
    def __OutputByte(self, id1, quantity):
        data = ''
        q = quantity
        for i in range(0, 8):
            if self.Outputs[id1+i] and q>0:
                data += '1'
            else:
                data += '0'
            q=q-1
        return int(data[::-1], 2)

    # Private
    # Function 2 (list of bits with some offset and range)
    def __InputByte(self, id1, quantity):
        data = ''
        q = quantity
        for i in range(0, 8):
            if self.Inputs[id1+i] and q>0:
                data += '1'
            else:
                data += '0'
            q=q-1
        return int(data[::-1], 2)

    # Private
    # Return register
    def __Register(self, i):
        if self.Registers[i] >= 0 and self.Registers[i] <= 65535:
            return self.Registers[i].to_bytes(2, byteorder='big', signed=False)
        else:
            return self.Registers[i].to_bytes(2, byteorder='big', signed=True)

    # Private
    # Return Input Register
    def __InputRegister(self, i):
        if self.InputRegisters[i] >= 0 and self.InputRegisters[i] <= 65535:
            return self.InputRegisters[i].to_bytes(2, byteorder='big', signed=False)
        else:
            return self.InputRegisters[i].to_bytes(2, byteorder='big', signed=True)

    # Private
    # Function 06 (06hex) Write Single Holding Register
    def __WriteRegister(self, ID, value):
        # Holding Registers
        # 40001-49999
        msg = [self.UnitID, 0x06]
        msg.extend((ID).to_bytes(2, byteorder='big'))
        self.Registers[ID] = value
        if 0 <= value <= 65535:
            msg.extend(value.to_bytes(2, byteorder='big', signed=False))
        else:
            msg.extend(value.to_bytes(2, byteorder='big', signed=True))
        return self.__crcMB(msg)

    # Private
    # Function 05 (05hex) Write Single Coil
    def __WriteCoil(self, ID, value):
        # Discrete Outputs
        # 00001-09999
        msg = [self.UnitID, 0x05]
        msg.extend((ID).to_bytes(2, byteorder='big'))
        if value:
            msg.extend([0xFF, 0x00])
            self.Outputs[ID] = True
        else:
            msg.extend([0x00, 0x00])
            self.Outputs[ID] = False
        return self.__crcMB(msg)

    # Private
    # Function 04 (04hex) Read Input Registers
    def __ReadIRegisters(self, startID, quantity):
        # Input Registers
        # 30001-39999
        msg = [self.UnitID, 0x04]
        msg.extend([(quantity*2)])
        for i in range(startID, startID + quantity):
            msg.extend(self.__InputRegister(i))
        return self.__crcMB(msg)

    # Private
    # Function 03 (03hex) Read Holding Registers
    def __ReadRegisters(self, startID, quantity):
        # Holding Registers
        # 40001-49999
        msg = [self.UnitID, 0x03]
        msg.extend([(quantity*2)])
        for i in range(startID, startID + quantity):
            msg.extend(self.__Register(i))
        return self.__crcMB(msg)

    # Private
    # Function 02 (02hex) Read Discrete Inputs
    def __ReadInput(self, startID, quantity):
        # Discrete Inputs
        # 10001-19999
        msg = [self.UnitID, 0x02]
        j = math.ceil(quantity / 8)
        msg.extend([j])
        lastBits = quantity
        lastID = startID
        for _ in range(0, j):
            msg.extend(self.__InputByte(lastID, lastBits).to_bytes(1, byteorder='big'))
            lastBits = lastBits - 8
            lastID = lastID + 8
        print(msg)
        return self.__crcMB(msg)

    # Private
    # Function 01 (01hex) Read Coils
    def __ReadOutput(self, startID, quantity):
        # Discrete Outputs
        # 00001-09999
        msg = [self.UnitID, 0x01]
        j = math.ceil(quantity / 8)
        msg.extend([j])
        lastBits = quantity
        lastID = startID
        for _ in range(0, j):
            msg.extend(self.__OutputByte(lastID, lastBits).to_bytes(1, byteorder='big'))
            lastBits = lastBits - 8
            lastID = lastID + 8
        return self.__crcMB(msg)
    

def main():
    print("## Micro Modbus class for workshop experiments.        ##")
    print("## Try to send data as a master or also as a slave.    ##")
    print("## For a list of actual methods use -h, --help         ##")
    print(help)
    pass

if __name__ == "__main__":
    main()

