# ----- A simple TCP client program in Python using send() function -----
from uModBus import uModBus
from time import sleep

# Obiekt modbus:
mb1 = uModBus()
mb1.UnitID = 21
# Init Client (Master / polling device)
mb1.TCPinit("127.0.0.1")

# Build requests:
reqF01 = mb1.requestBuild(UnitID=21, Function=1, Offset=0, Quantity=12)
print("Function 01 request: " + reqF01.hex())

reqF03 = mb1.requestBuild(UnitID=21, Function=3, Offset=0, Quantity=6)
print("Function 03 request: " + reqF03.hex())
while True:
    # Send request, receive and print response for Function 03:
    mb1.TCPsend(reqF01)
    FromServer_reqF01 = mb1.TCPread()
    print('Resp:')
    print(FromServer_reqF01)
    sleep(0.5)

    # Send request, receive and print response for Function 03:
    mb1.TCPsend(reqF03)
    FromServer_reqF03 = mb1.TCPread()
    print(FromServer_reqF03)
    sleep(0.5)
