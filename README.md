# uModbus
Micro Modbus class for workshop experiments - free, unfortunately bugged :) and also in continuation

The standart implemented with model from: https://www.simplymodbus.ca/ (website and content Copyright © 2020 Simply Modbus).
Tested in about 30% with Modbus Slave from: https://www.modbustools.com/ (tool and website content Copyright © 2020 Witte Software).  

Modbus TCP standard is easy, in some commisionings still in use by many measurement devices (but not only - control devices also!).
That is why it is good to know rules of this standard.

## Scope:
Class object what could be parametrized as Slave or Master
Main point - bridge between TCP/serial (Modbus) and data on PC oriented as object (message frames as lists in general on python side)

Minor points:
 - learn Modbus TCP standard (RTU comming soon)
 - prepare some easy tool for further testing (future target)
 - class should have Slave xor Master features be flexible in that way (soon)
 
## Testing:
Now prepared ModbusTCP tests with synchronous usage of TCP read/write socket usage.


## Example of use as Master
Send request TCP messages for information from slave devices. This is TCP client script.

The begining:
```python
# Object uModbus Create/Put address ID/IPv4 address:
mb1 = uModBus()
mb1.UnitID = 21
mb1.TCPinit("127.0.0.1")  # test on local
```

Now build a request - Function 3 - Read 6 Holding Registers starting with address "0":
```python
reqF03 = mb1.requestBuild(UnitID=22, Function=3, Offset=0, Quantity=6)
```

Then use reqest in an action (now TCP is the only way) - send and wait for response:
```python
mb1.TCPsend(reqF01)
FromServer_reqF01 = mb1.TCPread()
```

At the end Master needs to parse data into further program resources.
In reality slaves uses predefined addressed registers/inputs/outputs, so further answer parsers will come here soon (under construction).


## Example of use as Slave
Await for incoming TCP request messages and answer when ID address and crc fits.

The begining quite the same as in previous example:
```python
# Object uModbus Create/Put address ID/IPv4 address:
mb2 = uModBus()
mb2.UnitID = 22
mb2.TCPinit("127.0.0.1")  # test on local
```

Type as Slave and Wait for first connection:
```python
mb2.TCPslave()
mb2.TCPslaveAccept()
```

Wait for incoming message and answer to the Master (synchronous example in loop):
```python
while True:
    status = mb2.TCPslaveRead()
    if not status:
        mb2.TCPslaveResponse()
```

For the Slave device data should be parser automatically in case of writing function usage.

