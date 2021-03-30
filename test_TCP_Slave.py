from uModBus import uModBus

# Define modbus object - SLAVE:
mb2 = uModBus()

# Set some Discrete Input Values (10001-19999) DI:
mb2.Inputs[0] = True
mb2.Inputs[1] = False
mb2.Inputs[2] = True
mb2.Inputs[3] = True
mb2.Inputs[4] = False
mb2.Inputs[5] = False
mb2.Inputs[6] = False
mb2.Inputs[7] = True

# Set some Discrete Output Values (20001-29999) DQ:
mb2.Outputs[0] = False
mb2.Outputs[1] = True
mb2.Outputs[2] = True
mb2.Outputs[3] = True
mb2.Outputs[4] = True
mb2.Outputs[5] = False
mb2.Outputs[6] = False
mb2.Outputs[7] = False
mb2.Outputs[8] = False
mb2.Outputs[9] = False
mb2.Outputs[10] = False
mb2.Outputs[11] = False
mb2.Outputs[12] = False

# Set some Holding Register Values (40001-49999) MW:
mb2.Registers[0] = 9
mb2.Registers[1] = 8
mb2.Registers[2] = 7
mb2.Registers[3] = 6
mb2.Registers[4] = 5
mb2.Registers[5] = 4

# Set some Input Register Values (30001-39999) IW:
mb2.InputRegisters[0] = 22
mb2.InputRegisters[1] = 33
mb2.InputRegisters[2] = 44
mb2.InputRegisters[3] = 55
mb2.InputRegisters[4] = 66
mb2.InputRegisters[5] = 77

# Example of a SLAVE:
mb2.TCP_Init(ip="127.0.0.1", id=22, master=False)
while True:
    mb2.TCP_requestRead()
    mb2.TCP_responseSend()

