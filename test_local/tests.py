#!/usr/bin/env python3

from uModBus import uModBus
# import pytest
# import unittest

# Modbus objects initialization
# Slave (TCP server):
mb1 = uModBus()
mb1.UnitID = 21
mb1.TCPinit("127.0.0.1")
mb1.TCPslave()
# Master (TCP client):
mb2 = uModBus()
mb2.UnitID = 22
mb2.TCPinit("127.0.0.1")

# Slave data init
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


def test_read_HoldReg_1():
    # mb2 - master  /  mb1 - slave
    req = mb2.requestBuild(UnitID=21, Function=3, Offset=1, Quantity=4)
    mb2.TCPsend(req)
    mb1.TCPslaveAccept()
    mb1.TCPslaveRead()
    mb1.TCPslaveResponse()
    FromServer_req = mb2.TCPread()
    print("Response received...")
    print(FromServer_req)
    mb2.responseRead(FromServer_req, checkCRC=True, slaveID=21, offset=1)
    assert (
        0 == mb2.Registers[0] and
        mb1.Registers[1] == mb2.Registers[1] and
        mb1.Registers[2] == mb2.Registers[2] and
        mb1.Registers[3] == mb2.Registers[3] and
        mb1.Registers[4] == mb2.Registers[4] and
        0 == mb2.Registers[5]
    )


def test_read_HoldReg_2():
    mb2.clearData()
    # mb2 - master  /  mb1 - slave
    req = mb2.requestBuild(UnitID=21, Function=3, Offset=4, Quantity=3)
    mb2.TCPsend(req)
    mb1.TCPslaveAccept()
    mb1.TCPslaveRead()
    mb1.TCPslaveResponse()
    FromServer_req = mb2.TCPread()
    print("Response received...")
    print(FromServer_req)
    mb2.responseRead(FromServer_req, checkCRC=True, slaveID=21, offset=4)
    assert (
        0 == mb2.Registers[2] and
        0 == mb2.Registers[3] and
        mb1.Registers[4] == mb2.Registers[4] and
        mb1.Registers[5] == mb2.Registers[5] and
        mb1.Registers[6] == mb2.Registers[6] and
        0 == mb2.Registers[7] and
        0 == mb2.Registers[8]
    )


def test_read_InputReg_1():
    mb2.clearData()
    # mb2 - master  /  mb1 - slave
    req = mb2.requestBuild(UnitID=21, Function=4, Offset=1, Quantity=2)
    mb2.TCPsend(req)
    mb1.TCPslaveAccept()
    mb1.TCPslaveRead()
    mb1.TCPslaveResponse()
    FromServer_req = mb2.TCPread()
    print("Response received...")
    print(FromServer_req)
    mb2.responseRead(FromServer_req, checkCRC=True, slaveID=21, offset=1)
    assert (
        0 == mb2.InputRegisters[0] and
        mb1.InputRegisters[1] == mb2.InputRegisters[1] and
        mb1.InputRegisters[2] == mb2.InputRegisters[2] and
        0 == mb2.InputRegisters[3] and
        0 == mb2.InputRegisters[4]
    )


def test_read_InputReg_2():
    mb2.clearData()
    # mb2 - master  /  mb1 - slave
    req = mb2.requestBuild(UnitID=21, Function=4, Offset=2, Quantity=2)
    mb2.TCPsend(req)
    mb1.TCPslaveAccept()
    mb1.TCPslaveRead()
    mb1.TCPslaveResponse()
    FromServer_req = mb2.TCPread()
    print("Response received...")
    print(FromServer_req)
    mb2.responseRead(FromServer_req, checkCRC=True, slaveID=21, offset=2)
    assert (
        0 == mb2.InputRegisters[0] and
        0 == mb2.InputRegisters[1] and
        mb1.InputRegisters[2] == mb2.InputRegisters[2] and
        mb1.InputRegisters[3] == mb2.InputRegisters[3] and
        0 == mb2.InputRegisters[6] and
        0 == mb2.InputRegisters[7]
    )


def test_write_HoldReg_1():
    mb2.clearData()
    # mb2 - master  /  mb1 - slave
    mb2.Registers[2] = 22
    mb2.Registers[3] = 333
    mb2.Registers[4] = 4444
    # Write function has value papameter instead of quantity
    req = mb2.requestBuild(
        UnitID=21,
        Function=6,
        Offset=2,
        Val=mb2.Registers[2])
    mb2.TCPsend(req)
    mb1.TCPslaveAccept()
    mb1.TCPslaveRead()
    mb1.TCPslaveResponse()
    FromServer_req = mb2.TCPread()
    print("Response received...")
    print(FromServer_req)
    assert (
        mb1.Registers[2] == mb2.Registers[2]
    )


def test_write_HoldReg_2():
    mb2.clearData()
    # mb2 - master  /  mb1 - slave
    mb2.Registers[2] = 22
    mb2.Registers[3] = 333
    mb2.Registers[4] = 4444
    # Write function has value papameter instead of quantity
    req = mb2.requestBuild(
        UnitID=21,
        Function=6,
        Offset=3,
        Val=mb2.Registers[3])
    mb2.TCPsend(req)
    mb1.TCPslaveAccept()
    mb1.TCPslaveRead()
    mb1.TCPslaveResponse()
    FromServer_req = mb2.TCPread()
    print("Response received...")
    print(FromServer_req)
    assert (
        mb1.Registers[3] == mb2.Registers[3]
    )
