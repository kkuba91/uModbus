# ----- A simple TCP based server program in Python using send() function -----
from uModBus import uModBus

# Modbus object:
mb1 = uModBus()
mb1.UnitID = 21

# Set some values for Discrete Inputs (10001-19999) DI:
mb1.Inputs[0] = True
mb1.Inputs[1] = False
mb1.Inputs[2] = True

# Set some values for Discrete Outputs (20001-29999) DQ:
mb1.Outputs[0] = False
mb1.Outputs[1] = True
mb1.Outputs[2] = True
mb1.Outputs[3] = False
mb1.Outputs[4] = True

# Set some values for Memory Registers (16bt each) (40001-49999) MW:
mb1.Registers[0] = 9
mb1.Registers[1] = 8
mb1.Registers[2] = 7
mb1.Registers[3] = 6
mb1.Registers[4] = 5
mb1.Registers[5] = 4

# Set some values for Input Registers(30001-39999) IW:
mb1.InputRegisters[0] = 22
mb1.InputRegisters[1] = 33
mb1.InputRegisters[2] = 44
mb1.InputRegisters[3] = 55
mb1.InputRegisters[4] = 66
mb1.InputRegisters[5] = 77

# Init Modbus Object
mb1.TCPinit("127.0.0.1")

# Bind address, listen and wait for connection accepted
mb1.TCPslave()
mb1.TCPslaveAccept()

# Read and response loop
while True:
    status = mb1.TCPslaveRead()
    if not status:
        mb1.TCPslaveResponse()
        # value modification for 6th Memory Register
        mb1.Registers[5] = mb1.Registers[5] + 1


