from uModBus import uModBus

# Define modbus object:
mb1 = uModBus()
mb1.UnitID = 21

# Set some Discrete Input Values (10001-19999) DI:
mb1.Inputs[0] = True
mb1.Inputs[1] = False
mb1.Inputs[2] = True

# Set some Discrete Output Values (20001-29999) DQ:
mb1.Outputs[0] = False
mb1.Outputs[1] = True
mb1.Outputs[2] = True
mb1.Outputs[3] = True
mb1.Outputs[4] = True
mb1.Outputs[5] = False
mb1.Outputs[6] = False
mb1.Outputs[7] = False
mb1.Outputs[8] = False
mb1.Outputs[9] = False
mb1.Outputs[10] = False
mb1.Outputs[11] = False
mb1.Outputs[12] = False

# Set some Holding Register Values (40001-49999) MW:
mb1.Registers[0] = 9
mb1.Registers[1] = 8
mb1.Registers[2] = 7
mb1.Registers[3] = 6
mb1.Registers[4] = 5
mb1.Registers[5] = 4

# Set some Input Register Values (30001-39999) IW:
mb1.InputRegisters[0] = 22
mb1.InputRegisters[1] = 33
mb1.InputRegisters[2] = 44
mb1.InputRegisters[3] = 55
mb1.InputRegisters[4] = 66
mb1.InputRegisters[5] = 77

# MODBUS RTU ANSWER INTERPRET

# Answer for function nr 4 "Read Input Registers"
print('Request for function nr 4 "Read Input Registers: startID=0, quantity=2')
print(mb1.ReadIRegisters(startID=0, quantity=2))

# Answer for function nr 3 "Read Holding Registers"
print('\nRequest for function nr 3 "Read Holding Registers: startID=1, quantity=4')
print(mb1.ReadRegisters(startID=1, quantity=4))

# Answer for function nr 2 "Read Input Status"
print('\nRequest for function nr 2 "Read Input Status: startID=2, quantity=2')
print(mb1.ReadInput(startID=2, quantity=2))

# Answer for function nr 1 "Read Output Status"
print('\nRequest for function nr 1 "Read Output Status": startID=2, quantity=2')
print(mb1.ReadOutput(startID=2, quantity=2))

# Modbus CRC check
print('\nModbus CRC check for some byte sequence')
DataIn = [0x11, 0x04, 0x00, 0x08, 0x00, 0x01, 0xB2, 0x98]
print(mb1.check_crc(DataIn))

# Request construction examples
print('\nRequest construction examples')
print(mb1.requestBuild(UnitID=25, Function=1, Offset=100, Quantity=300))

# Request validation:
print('\noAnswer for: 0x15, 0x01, 0x00, 0x02, 0x00, 0x04, 0xB2, 0x98:')
DataIn = [0x15, 0x01, 0x00, 0x02, 0x00, 0x04, 0xB2, 0x98]
print(mb1.requestRead(data=DataIn, checkCRC=False))

print('\nAnswer for: 0x15, 0x03, 0x00, 0x02, 0x00, 0x02, 0xB2, 0x98:')
DataIn = [0x15, 0x03, 0x00, 0x01, 0x00, 0x02, 0xB2, 0x98]
print(mb1.requestRead(data=DataIn, checkCRC=False))

print('\nAnswer for: Write Single Coil (FC05):')
print(mb1.Outputs)
DataIn = [0x15, 0x05, 0x00, 0x03, 0xFF, 0x00, 0xB2, 0x98]
print(mb1.requestRead(data=DataIn, checkCRC=False))
print(mb1.Outputs)

print('\nAnswer for: Write Single Register (FC06):')
print(mb1.Registers)
DataIn = [0x15, 0x06, 0x00, 0x04, 0x01, 0x02, 0xB2, 0x98]
print(mb1.requestRead(data=DataIn, checkCRC=False))
print(mb1.Registers)
