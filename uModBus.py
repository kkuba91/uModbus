import socket
import math

class uModBus:
    """   Micro Modbus Object for Frame constructor   """
    def __init__(self):
        # Some typical data definition for modbus device
        self.type = 1
        self.UnitID = 2
        self.Inputs = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.Outputs = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.Registers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.InputRegisters = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.TCP = None
        self.TCP_IP = ""
        self.TCP_msg = []
        self.TCP_tx = 0
        self.TCP_length = 0
        self.TCP_clientConnected = None
        self.TCP_clientAddress = None
        self.TCP_request = None
        self.TCP_connected = False

    def TCPinit(self, ip):
        self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_IP = ip

    # Connect function with socker reinit for ModbusTCP port
    def TCPconnect(self):
        self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP.connect((self.TCP_IP, 502))

    def TCPmaster(self):
        self.TCP.connect((self.TCP_IP, 502))

    def TCPslave(self):
        self.TCP.bind((self.TCP_IP, 502))
        self.type = 2
        self.TCP.listen()

    def TCPslaveAccept(self):
        (self.TCP_clientConnected, self.TCP_clientAddress) = self.TCP.accept()

    def TCPslaveRead(self):
        try:
            dataFromMaster = list(bytes(self.TCP_clientConnected.recv(1024)))
            print("ALL packets received:")
            print(list(dataFromMaster))
            tx1 = dataFromMaster.pop(0)
            tx2 = dataFromMaster.pop(0)
            self.TCP_tx = int.from_bytes([tx1, tx2], byteorder='big', signed=False)
            dataFromMaster.pop(0)
            dataFromMaster.pop(0)
            l1 = dataFromMaster.pop(0)
            l2 = dataFromMaster.pop(0)
            self.TCP_length = int.from_bytes([l1, l2], byteorder='big', signed=False)
            print("Significant packets received:")
            print(list(dataFromMaster))
            self.TCP_request = dataFromMaster
            return 0
        except BaseException as e:
            print(e)
            self.TCPslaveAccept()
            return -1

    def TCPslaveResponse(self):
        try:
            self.TCP_msg.clear()
            dataToServer = self.requestRead(self.TCP_request, False)
            dataToServer.pop()
            dataToServer.pop()
            # print("Significant packets sent:")
            # print(dataToServer)
            self.TCP_length = len(dataToServer)
            self.TCP_msg.extend(self.TCP_tx.to_bytes(2, byteorder='big'))
            self.TCP_msg.extend([0x00, 0x00])
            self.TCP_msg.extend(self.TCP_length.to_bytes(2, byteorder='big'))
            self.TCP_msg.extend(dataToServer)
            self.TCP_clientConnected.send(bytearray(self.TCP_msg))
            print("All packets sent:")
            print(self.TCP_msg)
            return 0
        except BaseException as e:
            print(e)
            self.TCPslaveAccept()
            return -1


    def TCPsend(self, data):
        if not self.TCP_connected:
            self.TCPconnect()
            self.TCP_connected = True
        self.TCP_msg.clear()
        self.TCP_tx = self.TCP_tx + 1
        self.TCP_msg.extend(self.TCP_tx.to_bytes(2, byteorder='big'))
        self.TCP_msg.extend([0x00, 0x00])
        self.TCP_length = len(data)
        self.TCP_msg.extend(self.TCP_length.to_bytes(2, byteorder='big'))
        try:
            self.TCP_msg.extend(data)
            self.TCP.send(bytearray(self.TCP_msg))
            # print("All packets sent:")
            # print(self.TCP_msg)
        except BaseException as e:
            # self.TCP.connect((self.TCP_IP, 502))
            print(e)

    def TCPread(self):
        msg = None
        try:
            msg = list(self.TCP.recv(1024))
            msg.pop(0)
            msg.pop(0)
            msg.pop(0)
            msg.pop(0)
            msg.pop(0)
            msg.pop(0)
            self.TCP.close()
            self.TCP_connected = False
            return list(bytes(msg))
        except BaseException as e:
            print(e)
            return list(bytes([0x00]))

    def calc_crc(self, data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for i in range(8):
                if ((crc & 1) != 0):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def check_crc(self, data):
        tempCRC = [0, 0]
        tempCRC[0] = data.pop()
        tempCRC[1] = data.pop()
        data = self.crcMB(data)
        if tempCRC[0] == data.pop() and tempCRC[1] == data.pop():
            return True
        else:
            return False

    def crcMB(self, data):
        bb = self.calc_crc(data).to_bytes(2, byteorder="little")
        data.extend(bb)
        return data

    def requestBuild(self, UnitID, Function, Offset, Quantity):
        msg = [UnitID, Function]
        tempBytes = Offset.to_bytes(2, byteorder='big', signed=False)
        msg.extend([tempBytes[0], tempBytes[1]])
        tempBytes = Quantity.to_bytes(2, byteorder='big', signed=False)
        msg.extend([tempBytes[0], tempBytes[1]])
        return bytearray(self.crcMB(msg))

    # Read ModbusTCP message without prefix
    # Returning answer message
    def requestRead(self, data, checkCRC):
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
                return self.ReadOutput(offset-1, quantity)
            if data[1] == 0x02:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.ReadInput(offset-1, quantity)
            if data[1] == 0x03:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.ReadRegisters(offset-1, quantity)
            if data[1] == 0x04:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                quantity = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.ReadIRegisters(offset-1, quantity)
            if data[1] == 0x05:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                if data[4] == 0xFF and data[5] == 0x00:
                    value = True
                if data[4] == 0x00 and data[5] == 0x00:
                    value = False
                if data[5] == 0x00 and (data[4] == 0xFF or data[4] == 0x00):
                    return self.WriteCoil(offset-1, value)
                else:
                    return -1
            if data[1] == 0x06:
                offset = 1 + int.from_bytes([data[2], data[3]], byteorder='big', signed=False)
                val = int.from_bytes([data[4], data[5]], byteorder='big', signed=False)
                return self.WriteRegister(offset-1, val)
        else:
            return -1

    # Warning this was the simplest/worst way to send boolean data represented by whole 16bit registers
    # In fact of Modbus standard, was not used in library anymore
    # this includes Input() and Output() functions
    def Input(self, i): # Wrong way - not used
        if self.Inputs[i]:
            return [0x00, 0xFF]
        else:
            return [0x00, 0x00]

    def Output(self, i): # Wrong way - not used
        if self.Outputs[i]:
            return [0x00, 0xFF]
        else:
            return [0x00, 0x00]

    # Right way for Function 1 (list of bits with some offset and range)
    def OutputByte(self, id1, quantity):
        data = ''
        q = quantity
        for i in range(0, 8):
            if self.Outputs[id1+i] and q>0:
                data += '1'
            else:
                data += '0'
            q=q-1
        return int(data[::-1], 2)

    # Right way for Function 2 (list of bits with some offset and range)
    def InputByte(self, id1, quantity):
        data = ''
        q = quantity
        for i in range(0, 8):
            if self.Inputs[id1+i] and q>0:
                data += '1'
            else:
                data += '0'
            q=q-1
        return int(data[::-1], 2)

    # Return register
    def Register(self, i):
        if self.Registers[i] >= 0 and self.Registers[i] <= 65535:
            return self.Registers[i].to_bytes(2, byteorder='big', signed=False)
        else:
            return self.Registers[i].to_bytes(2, byteorder='big', signed=True)

    # Return Input Register
    def InputRegister(self, i):
        if self.InputRegisters[i] >= 0 and self.InputRegisters[i] <= 65535:
            return self.InputRegisters[i].to_bytes(2, byteorder='big', signed=False)
        else:
            return self.InputRegisters[i].to_bytes(2, byteorder='big', signed=True)

    #   Function 06 (06hex) Write Single Holding Register
    def WriteRegister(self, ID, value):
        # Holding Registers
        # 40001-49999
        msg = [self.UnitID, 0x06]
        msg.extend((ID).to_bytes(2, byteorder='big'))
        self.Registers[ID] = value
        if 0 <= value <= 65535:
            msg.extend(value.to_bytes(2, byteorder='big', signed=False))
        else:
            msg.extend(value.to_bytes(2, byteorder='big', signed=True))
        return self.crcMB(msg)

    #   Function 05 (05hex) Write Single Coil
    def WriteCoil(self, ID, value):
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
        return self.crcMB(msg)

#   Function 04 (04hex) Read Input Registers
    def ReadIRegisters(self, startID, quantity):
        # Input Registers
        # 30001-39999
        msg = [self.UnitID, 0x04]
        msg.extend(startID.to_bytes(2, byteorder='big'))
        msg.extend((quantity * 2).to_bytes(2, byteorder='big'))
        for i in range(startID, startID + quantity):
            msg.extend(self.InputRegister(i))
        return self.crcMB(msg)

#   Function 03 (03hex) Read Holding Registers
    def ReadRegisters(self, startID, quantity):
        # Holding Registers
        # 40001-49999
        msg = [self.UnitID, 0x03]
        msg.extend([(quantity*2)])
        for i in range(startID, startID+quantity):
            msg.extend(self.Register(i))
        return self.crcMB(msg)

#   Function 02 (02hex) Read Discrete Inputs
    def ReadInput(self, startID, quantity):
        # Discrete Inputs
        # 10001-19999
        msg = [self.UnitID, 0x02]
        msg.extend(startID.to_bytes(2, byteorder='big'))
        msg.extend((quantity * 2).to_bytes(2, byteorder='big'))
        j = math.ceil(quantity / 8)
        # for i in range(startID, startID + quantity):
        #    msg.extend(self.Input(i))
        lastBits = quantity
        lastID = startID
        for i in range(0, j-1):
            msg.extend(self.OutputByte(lastID, lastBits).to_bytes(1, byteorder='big'))
            lastBits = lastBits - 8
            lastID = lastID + 8
        return self.crcMB(msg)

# Function 01 (01hex) Read Coils
    def ReadOutput(self, startID, quantity):
        # Discrete Outputs
        # 00001-09999
        msg = [self.UnitID, 0x01]
        # msg.extend(startID.to_bytes(2, byteorder='big')) - brak id w odpowiedzi
        # msg.extend((quantity * 2).to_bytes(1, byteorder='big'))
        # for i in range(startID, startID + quantity):
        #    msg.extend(self.Output(i))
        j = math.ceil(quantity / 8)
        msg.extend(j.to_bytes(1, byteorder='big'))
        lastBits = quantity
        lastID = startID
        for i in range(0, j):
            msg.extend(self.OutputByte(lastID, lastBits).to_bytes(1, byteorder='big'))
            lastBits = lastBits - 8
            lastID = lastID + 8
        return self.crcMB(msg)
