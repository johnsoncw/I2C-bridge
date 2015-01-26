#!/usr/bin/env python
# encoding: utf-8
"""
Created by Chris Johnson, 2015.

This script reads a DS18B20 temperature sensor via a DS2484 via a BusPirate.
Copyright (C) 2015  Chris Johnson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
import bus_pirate
from tracer import *


class I2cFacade:
    """ The API in the embedded MCU world that interfaces to I2C """

    class I2cWriteCommand():
        def __init__(self, addr, code, name=None):
            self.name = name
            self.addr = addr
            self.code = code

        def __call__(self, data=None):
            if self.name is not None:
                tracer("I2cWriteCommand : " + self.name)
            cmd = bytearray()
            cmd.extend(self.addr)
            cmd.extend(self.code)
            if data is not None:
                cmd.extend(data)
            bus_pirate.start_i2c_transaction()
            bus_pirate.bulk_write(cmd)
            bus_pirate.end_i2c_transaction()

    class I2cReadCommand():
        def __init__(self, addr, prep=None, name=None):
            self.addr = addr
            self.prep = prep
            self.name = name

        def __call__(self, num=1):
            if self.name is not None:
                tracer("I2cReadCommand : " + self.name)
            if self.prep is not None:
                self.prep()
            bus_pirate.start_i2c_transaction()
            data_read = bus_pirate.read_i2c(self.addr, num)
            bus_pirate.end_i2c_transaction()
            return data_read


class DS2484:
    class OWWriteCommand():
        def __init__(self, code, name=None):
            self.code = code
            self.name = name

        def __call__(self, id=None, data=None):
            if self.name is not None:
                tracer("  Send OW : " + self.name)
            cmd = bytearray()
            if id is not None:
                cmd.extend(DS18B20.MATCH_DEV)
                cmd.extend(id)
            else:
                cmd.extend(DS18B20.MATCH_ALL)
            cmd.extend(self.code)
            if data is not None:
                cmd.extend(data)
            DS2484.ow_write(cmd)

    class OWReadCommand():
        def __init__(self, code, num_to_read=1, name=None):
            self.code = code
            self.num_to_read = num_to_read
            self.name = name

        def __call__(self, dev_id=None):
            if self.name is not None:
                tracer("  Read OW : " + self.name)
            cmd = bytearray()
            if dev_id is not None:
                cmd.extend(DS18B20.MATCH_DEV)
                cmd.extend(dev_id)
            else:
                cmd.extend(DS18B20.MATCH_ALL)
            cmd.extend(self.code)
            DS2484.ow_write(cmd)
            return DS2484.ow_get_data(self.num_to_read)

    R_ADDR = b"\x31"  # DS2484 slave -> BP master
    W_ADDR = b"\x30"  # BP master -> DS2484 slave

    # Performs a global reset of device state machine logic. Terminates
    # any ongoing 1-Wire communication. Parameter: none
    reset = I2cFacade.I2cWriteCommand(W_ADDR, b"\xF0", "DS2484 reset")

    # OW Read pointer source
    class Register:
        CONFIG = b"\xC3"
        PORT_CONFIG = b"\xB4"
        STATUS = b"\xF0"
        DATA = b"\xE1"

    # Reads a DS2484 register via the I2C bus.
    # Parameter: Register, number of bytes to read
    prep_read_status_register = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\xE1" + Register.STATUS)

    read_status_register = I2cFacade.I2cReadCommand(
        R_ADDR, prep_read_status_register, "DS2484 read status register")

    prep_read_data_register = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\xE1" + Register.DATA)

    read_data_register = I2cFacade.I2cReadCommand(
        R_ADDR, prep_read_data_register, "DS2484 read data register")

    # Writes a new device configuration byte. The new settings take
    # effect immediately. Note: When writing to the Device Configuration
    # register, the new data is accepted only if the upper nibble (bits
    # 7 to 4) is the one’s complement of the lower nibble (bits 3 to
    # 0). When read, the upper nibble is always 0h.
    # Parameter: conf byte
    write_config = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\xD2", "DS2484 write config")

    # Updates the selected 1-Wire port parameter, which affects the
    # 1-Wire timing or pull up resistor selection. See OwPortCtrlSel
    # for the control byte format. Note: Upon a power-on reset or after
    # a Device Reset command, the parameter default values apply.
    # param: OwPortCtrlSel
    adjust_ow_port = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\xC3", "DS2484 adjust port")

    # Generates a 1-Wire reset/presence-detect cycle at the 1-Wire line
    # (Figure 4). The state of the 1-Wire line is sampled at tSI and
    # tMSP and the result is reported to the host processor through the
    # Status register bits PPD and SD.
    # Parameter: none
    ow_reset = I2cFacade.I2cWriteCommand(W_ADDR, b"\xB4", "DS2484 reset OW")

    # Generates a single 1-Wire time slot with a bit value “V” as
    # specified by the bit byte at the 1-Wire line. A V value of
    # _OW_SINGLE_BIT_VAL. In either case, the logic level at the 1-Wire
    # line is tested at tMSR and SBR is updated.
    # Parameter: OwSingleBitVal
    ow_single_bit = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\x87", "DS2484 send OW single bit")

    # To write commands or data to the 1-Wire line. Equivalent to
    # executing eight 1-Wire Single Bit commands, but faster due to less
    # I2C traffic.
    # Parameter: data byte
    ow_write_byte = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\xA5", "DS2484 send OW write byte")

    # Generates eight read-data time slots on the 1-Wire line and stores
    # result in the Read Data register. Status register (for busy
    # polling). Note: To read the data byte received from the 1-Wire
    # line, issue the Set Read Pointer command and select the Read Data
    # register. Then access the DS2484 in read mode.
    # Parameter: None
    get_ow_byte_into_data_reg = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\x96", "DS2484 read 8 OW bits into data register")

    # Generates three time slots: two read time slots and one write time
    # slot at the 1-Wire line. The type of write time slot depends on
    # the result of the read time slots and the direction byte.
    # Parameter: OwSingleBitVal
    ow_triplet = I2cFacade.I2cWriteCommand(
        W_ADDR, b"\x78", "DS2484 OW triplet")

    # One wire port control parameter is built by ORing OwPortCtrl,
    # OwPortVal and the value which makes up the least significant
    # 4 bits. See data sheet, page 13 for the meaning of each value bit
    # combination.
    class OwPortCntr:
        RSTL = b"\x00"
        MSP = b"\x20"
        WOL = b"\x40"
        REC0 = b"\x60"  # OD flag ignored
        WPU = b"\x80"  # OD flag ignored

    class OwPortVal:
        STD = b"\x00"  # applies to standard speed
        OVR = b"\x10"  # applies to overdrive speed

    class OwSingleBitVal:
        ZERO = b"\x00"
        ONE = b"\x80"

    class OwConfig:
        APU_ON = 0x01
        APU_OFF = 0x10
        PDN_ON = 0x02
        PDN_OFF = 0x20
        SPU_ON = 0x04
        SPU_OFF = 0x40
        OWS_ON = 0x08
        OWS_OFF = 0x80

    class Status:
        def __init__(self, status_byte):
            self.triplet_dir = status_byte & 0x80
            self.triplet_tsb = status_byte & 0x40
            self.sbr = status_byte & 0x20
            self.rst = status_byte & 0x10
            self.ll = status_byte & 0x08
            self.sd = status_byte & 0x04
            self.ppd = status_byte & 0x02
            self.owb = status_byte & 0x01

        @staticmethod
        def str(status):
            s = "DS2484 Status = "
            s += "DIR " if status.triplet_dir else ""
            s += "TSB " if status.triplet_tsb else ""
            s += "SBR " if status.sbr else ""
            s += "RST " if status.rst else ""
            s += "LL^ " if status.ll else "LLv "
            s += "SD " if status.sd else ""
            s += "PPD " if status.ppd else ""
            s += "OWB " if status.owb else ""
            return s

    @staticmethod
    def init():
        tracer("DS2484 init")
        DS2484.reset()

    @staticmethod
    def ow_write(data):
        DS2484.ow_new_transaction()
        for b in data:
            to_send = bytes([b])
            DS2484.ow_write_byte(to_send)
            time.sleep(0.01)

    @staticmethod
    def ow_get_data(num_to_read):
        data = bytearray()
        for _ in range(num_to_read):
            DS2484.ow_wait_until_idle()
            DS2484.get_ow_byte_into_data_reg()
            DS2484.prep_read_data_register()
            data.extend(DS2484.read_data_register())
        return data

    @staticmethod
    def ow_wait_until_idle():
        tracer("ow_wait_until_idle")
        while True:
            tracer("read status")
            DS2484.prep_read_status_register()
            stat_reg = DS2484.read_status_register(1)
            status = DS2484.Status(stat_reg[0])
            tracer(status.str(status))
            if status.owb is 0:
                break
            else:
                time.sleep(0.05)

    @staticmethod
    def ow_new_transaction():
        DS2484.ow_wait_until_idle()
        DS2484.ow_reset()
        DS2484.ow_wait_until_idle()


class DS18B20():
    # Matches and selects a one wire device by its 64 bit 'ROM' id .
    MATCH_DEV = b"\x55"  # parameter: 8 bytes or ROM id

    # Matches all devices which may be good to initiate a temperature
    # measurement but not so useful for a read because all devices would
    # respond at the same time.
    MATCH_ALL = b"\xCC"  # parameter: None

    # Initiates temperature measurement by devices on the One Wire bus.
    # If id is specified in the call just that one device is selcted, otherwise
    # all devices are address. The measurements are copied to the first 2 bytes
    # of the scratch pad in the device(s).
    measure_temperature = DS2484.OWWriteCommand(
        b"\x44", "DS18B20 measure temperature")

    # Read temperature from scratch pad.
    read_scratch = DS2484.OWReadCommand(
        b"\xBE", 2, "DS18B20 read scratch pad")

    configured = False

    @staticmethod
    def init():
        tracer("DS18B20 init")
        DS2484.write_config(
            bytes([DS2484.OwConfig.APU_ON |
                   DS2484.OwConfig.PDN_OFF |
                   DS2484.OwConfig.SPU_OFF |
                   DS2484.OwConfig.OWS_OFF]))

    @staticmethod
    def measure_temp(id=None):
        tracer("Measure temperature.")
        DS18B20.measure_temperature(id)
        time.sleep(0.5)

    @staticmethod
    def print_temp(id):
        tracer("Get temperature from DS18B20 device id=[ ", False)
        for b in id:
            tracer(format(b, '02x') + " ", False)
        tracer("]")
        data = DS18B20.read_scratch(id)
        temp_c = ((data[1] << 8) + data[0]) * 0.0625
        print("temp C = " + str(temp_c))
        print("temp F = " + str((temp_c * 1.8) + 32))
        return temp_c


if __name__ == '__main__':
    bus_pirate.init("COM15", 115200)
    bus_pirate.enter_i2c_mode()
    try:
        DS2484.init()
        DS18B20.init()
        id1 = [0x28, 0x23, 0x49, 0x83, 0x06, 0x00, 0x00, 0x6B]
        DS18B20.measure_temp(id1)
        DS18B20.print_temp(id1)
        id2 = [0x28, 0xa9, 0xe8, 0x83, 0x06, 0x00, 0x00, 0xb0]
        DS18B20.measure_temp(id2)
        DS18B20.print_temp(id2)
    except Exception as e:
        print(e)
    bus_pirate.end()
