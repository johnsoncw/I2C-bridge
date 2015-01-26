#!/usr/bin/env python
# encoding: utf-8
"""
Created by Chris Johnson, 2015.

This module is a limited Bus Pirate API.
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
import serial
from tracer import *
from builtins import range


class BpCommand:
    """ What's needed to generally send a command to the Bus Pirate. """
    def __init__(self, code, required_response=None, name=None):
        self.code = code
        self.required = required_response
        self.name = name

    def __call__(self):
        if self.name is not None:
            tracer("  BusPirate : " + self.name)
        execute_bp_command(self.code, self.required)


class BpExtCommand(BpCommand):
    """ A command that can modify the command byte when invoked. """
    def __call__(self, lower_nibble=0):
        if self.name is not None:
            tracer("  BusPirate : " + self.name)
        return execute_bp_command(
            bytes([self.code[0] | lower_nibble]), self.required)


I2C_START_BIT = b"\x02"
I2C_STOP_BIT = b"\x03"
I2C_READ_BYTE = b"\x04"
I2C_ACK = b"\x06"
I2C_NACK = b"\x07"
# bulk 1-16 bytes, lower nibble = count - 1 (i.e 0 == 1 byte)
send_i2c_bulk = BpExtCommand(b"\x10", None, "send bulk")
# lower nibble POWER, PULL_UPS bits OR'ed as required
config_i2c_peripherals = BpExtCommand(b"\x40", None, "set I2C peripherals")
I2C_POWER = 0x08
I2C_PULL_UPS = 0x04
# lower nibble Speed
set_i2c_speed = BpExtCommand(b"\x60", None, "set I2C speed")
I2C_SPEED_400KHZ = 0x03
I2C_SPEED_100KHZ = 0x02
I2C_SPEED_50KHZ = 0x01
I2C_SPEED_5KHZ = 0x00
BULK = 0x10

set_binary_mode = BpCommand(b"\x00", b"BBIO1", "binary mode")
set_i2c_mode = BpCommand(b"\x02", b"I2C1", "I2C mode")
set_uart_mode = BpCommand(b"\x03", None, "UART mode")
set_ow_mode = BpCommand(b"\x04", b"1W01", "one wire mode")
set_raw_mode = BpCommand(b"\x05", b"RAW1", "raw mode")
reset = BpCommand(b"\x0F", None, "reset")

bp_port = None
binary_mode = None
i2c_mode = None


def init(port, port_speed):
    """ Configure the Bus Pirate communications channel

    :param port: The port to use e.g. windows com port
    :param port_speed: The com port speed
    """
    tracer("BusPirate init")
    global bp_port, binary_mode, i2c_mode
    bp_port = serial.Serial(port, port_speed)
    binary_mode = False
    i2c_mode = False


def bulk_write(data):
    """ Send up to 16 bytes to the Bus Pirate I2C bus.

    :param data: an iterable collection of bytes 1-16 bytes long.

    The bulk write has the advantage that the entire sequence can often be sent
    between a start and end transaction.
    """
    send_len = len(data)
    if send_len > 16:
        end("ERROR: Bulk send to BP > 16 bytes")
    # Note: The number in the lower nibble is 1 less than length to send,
    # e.g. 0 means send 1 byte
    send_data = bytearray()
    send_data.append(BULK | (send_len - 1))
    send_data.extend(data)
    discard_input()
    port_write(send_data)
    trace_write_data(send_data[1:])
    # The command as well as the data must be acknowledged with a
    # read handshake to the Bus Pirate, hence data send_length + 1 reads.
    for _ in range(send_len + 1):
        read_byte()


def read_i2c(addr, num_to_read=1):
    """ Read bytes from a device on the I2C bus connected to the Bus Pirate.

    :param addr: I2C address to read from
    :param num_to_read: number of bytes to read
    :return: bytes read

    The Bus Pirate must be told whether to ack or nack each I2C read because
    it does not know how many reads are being done. To conform to the I2C spec
    each byte reads should be 'ack'ed except the last one which should be
    'nack'ed so that the device knows the reading phase is over.
    """
    cmd = bytearray()
    cmd.extend(addr)
    bulk_write(cmd)
    data = bytearray()
    for i in range(num_to_read):
        port_write(I2C_READ_BYTE)
        data.extend(read_byte())
        if i > 1:
            bp_port.write(I2C_ACK)
            # trace_data("    [ ack ] ", I2C_ACK)
            read_byte()  # the BP handshake for the command to send an ack
        else:
            bp_port.write(I2C_NACK)
            # trace_data("    [ nack ] ", I2C_NACK)
            read_byte()  # the BP handshake for the command to send an nack
    trace_read_data(data)
    return data


def discard_input():
    """ Empty the port data waiting to be read """
    global bp_port
    while bp_port.inWaiting():
        bp_port.read(1)


def enter_i2c_mode():
    """ Put Bus Pirate into I2C mode """
    global i2c_mode
    if not i2c_mode:
        enter_binary_mode()
        set_i2c_mode()
        i2c_mode = True
        config_i2c_peripherals(I2C_POWER | I2C_PULL_UPS)
        set_i2c_speed(I2C_SPEED_100KHZ)


def enter_binary_mode():
    """ Put Bus Pirate into binary mode """
    global binary_mode
    if not binary_mode:
        binary_mode = True
        reset()
        # TODO: Improve binary mode sensitive startup sequence if possible
        bp_port.write(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        time.sleep(0.1)
        set_binary_mode()


def cleanup():
    """ Put the Bus Pirate back to interactive mode """
    global binary_mode
    if binary_mode:
        binary_mode = False
        tracer("*** BusPirate Cleanup ***")
        try:
            port_write(b"\x00")
            reset()
        except Exception as e:
            print(e)
        set_uart_mode()


def start_i2c_transaction():
    tracer("  { -- i2c transaction --")
    discard_input()
    port_write(I2C_START_BIT)
    read_byte()


def end_i2c_transaction():
    tracer("  }")
    discard_input()
    port_write(I2C_STOP_BIT)
    read_byte()


def execute_bp_command(code, required):
    """ Actions a command and if required checks the response

    :param code: Command code
    :param required: Expected response
    """
    discard_input()
    port_write(code)
    trace_write_data(code)
    if required is not None:
        resp_check = bytearray()
        for i in range(len(required)):
            resp_check.extend(read_byte())
        trace_read_data(resp_check)
        if resp_check != required:
            end("  << " + str(resp_check) +
                " {*** FAILURE ***, Expected response to cmd " +
                str(code) + " was " + str(required) + "}")
    else:
        read_byte()


def end(message="Done"):
    """ Prints out a message and puts the Bus Pirate in interactive mode.

    :param message: Message to print out
    """
    tracer(message)
    cleanup()
    exit()


def port_write(data):
    # trace_data("    => ", data)
    bp_port.write(data)


def port_read():
    data = bp_port.read(1)
    # trace_data("      <= ", data)
    return data


def read_byte():
    """ Read a single byte of data from the Bus Pirate.

    :return: a single byte

    Up to 1s is given for the Bus Pirate to respond and provide data to read.
    If data us not available after 1s an exception is raised.
    """
    global bp_port
    num_waiting = bp_port.inWaiting()
    for _ in range(100):
        if num_waiting > 0:
            break
        time.sleep(0.01)
        num_waiting = bp_port.inWaiting()
    if num_waiting < 1:
        raise BaseException("ERROR: No response")
    return port_read()
