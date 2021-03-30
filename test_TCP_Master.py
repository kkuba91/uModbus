from uModBus import uModBus

# Example of MASTER:
mb1 = uModBus()
mb1.TCP_Init(ip="127.0.0.1", id=23, master=True)
while True:
    mb1.TCP_requestSend(UnitID=25, Function=3, Offset=1, Quantity=5, ForceData=None)
    mb1.TCP_responseRead()
    print(
        mb1.Registers[0], " ", mb1.Registers[1], " ", 
        mb1.Registers[2], " ", mb1.Registers[3], " ", 
        mb1.Registers[4], " ", mb1.Registers[5] )

    mb1.TCP_requestSend(UnitID=25, Function=4, Offset=0, Quantity=5, ForceData=None)
    mb1.TCP_responseRead()
    print(
        mb1.InputRegisters[0], " ", mb1.InputRegisters[1], " ", 
        mb1.InputRegisters[2], " ", mb1.InputRegisters[3], " ", 
        mb1.InputRegisters[4], " ", mb1.InputRegisters[5] )

    mb1.TCP_requestSend(UnitID=25, Function=2, Offset=1, Quantity=5, ForceData=None)
    mb1.TCP_responseRead()
    print(
        mb1.Inputs[0], " ", mb1.Inputs[1], " ", 
        mb1.Inputs[2], " ", mb1.Inputs[3], " ", 
        mb1.Inputs[4], " ", mb1.Inputs[5] )

    mb1.TCP_requestSend(UnitID=25, Function=1, Offset=3, Quantity=5, ForceData=None)
    mb1.TCP_responseRead()
    print(
        mb1.Outputs[0], " ", mb1.Outputs[1], " ", 
        mb1.Outputs[2], " ", mb1.Outputs[3], " ", 
        mb1.Outputs[4], " ", mb1.Outputs[5] )

    mb1.TCP_requestSend(UnitID=25, Function=5, Offset=1, Quantity=1, ForceData=True)
    mb1.TCP_responseRead()
    print(
        mb1.Outputs[0], " ", mb1.Outputs[1], " ", 
        mb1.Outputs[2], " ", mb1.Outputs[3], " ", 
        mb1.Outputs[4], " ", mb1.Outputs[5], "\n\n" ) 

    mb1.TCP_requestSend(UnitID=25, Function=6, Offset=1, Quantity=1, ForceData=9988)
    mb1.TCP_responseRead()
    print(
        mb1.Registers[0], " ", mb1.Registers[1], " ", 
        mb1.Registers[2], " ", mb1.Registers[3], " ", 
        mb1.Registers[4], " ", mb1.Registers[5], "\n\n")
