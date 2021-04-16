[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/kkuba91/uModbus/LICENSE)
[![Language: Python](https://img.shields.io/badge/python-%3E%3D3.7-blue)](https://github.com/kkuba91/uModbus)

# uModbus
#### Micro Modbus class for workshop experiments - free, unfortunately bugged yet :) but in development (F15 and F16 not implmented).

##### The standard implemented with model from: https://www.simplymodbus.ca/  (website and content Copyright © 2020 Simply Modbus).

##### Tested in about 50% by Modbus Slave/Master from: https://www.modbustools.com/  (tool and website content Copyright © 2020 Witte Software).  

This module was created for private purpose of learning python and modbus protocol.

It includes standard python3 modules: `socket`, `math`, `time`

Modbus TCP standard is relatively easy. In some commisionings still in use by many measurement devices (but not only - control devices uses it too).
That is why it is good to know the protocol structure. 

Dependent on application there are some related kinds of the standard: ModbusTCP, ModbusRTU, ModbusRTU over TCP, Modbus ASCII; This module was mainly related with the first one (most pompular usage).


## Scope:
Class object what could be parametrized as Slave or Master in the `TCP_Init()` method.


#### Main point:

- bridge between Modbus devices by data oriented objects on PC program (in general, the lists, in python script)


#### Minor points:

 - learn python, Modbus TCP standard (RTU not prepared)
 - prepare some easy tool for further testing
 - class should have Slave xor Master features, be flexible in that way (script could just have many uModbus instances for In/Out communication)


## Testing:
Now prepared ModbusTCP tests with synchronous requests of TCP read/write at ethernet socket.


## Warning
Requests must reach created elements inside the modbus object lists. So if the request ask for data outside the prepared ranges (inside constructor) function would return an exception and not accomplish.


## Example of use as Master
Send request TCP messages for information from slave devices. This is TCP client script.
The begining:

```python
mb1 = uModBus()    # Modbus Object
# Then specify as TCP class with other data, ex.:
mb1.TCP_Init(ip="127.0.0.1", id=23, master=True)
```

Now build a request - Function 3 - Read 5 Holding Registers starting with address "1".

Should have two functions: first for packet sending, second for receiving and parsing data:
```python
mb1.TCP_requestSend(UnitID=25, Function=3, Offset=1, Quantity=5, ForceData=None)
mb1.TCP_responseRead()
```
And this is all. The scope and purpose depends on Your needs now.

Simple preffered usage for functions above is to put then inside loop (ex. while).


## Example of use as Slave
Await for incoming TCP request messages and answer when ID address and crc fits.

The begining quite the same as in previous example:
```python
# Object uModbus Create/Put ID/IPv4 address:
mb2 = uModBus()
mb2.TCP_Init(ip="127.0.0.1", id=22, master=False)  # test on local
```
Script above uses socket listen() -> accept() functions, so they are called synchronous.

Data inside modbus object should change independent (by asynchronous functions) in best way. But here for testing purpose everything works synchronously.

So Slave Read-Request then Answer-The Respond are below (for better understanding put inside while loop, for the best inside asynchromous calling):
```python
while True:
    mb2.TCP_requestRead()
    mb2.TCP_responseSend()
```

The both functions shall be used always next to each other. Because the Slave device data could be parsed (this mechanism located inside second function).

