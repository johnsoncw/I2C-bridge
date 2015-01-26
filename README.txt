
This program reads a DS18B20 temperature sensor via a DS2484 via a BusPirate.
----------------------------------------------------------------------------

The purpose of this program is to explore the feasability of using a DS2484
(which is an I2C to 1-Wire protocol bridge), to read temperature measurements
from a number of DS18B20 devices (which are 1-wire temperature sensor devices).
    Python 3.4 was used for the prototype code here.
    I used 'Intellij idea' to develop the python code.
    Eclipse and the open-source, Cross ARM GCC tool chain, is being used for
    the embedded code development.

The 1-Wire protocol is a timing sensitive protocol for which library support
is rare, whereas the I2C protocol is far better supported for embedded
processors and is not subject to the same intensive time sensitive bit
twiddling. So the DS2484 may be useful to simplify interfacing to the 1-Wire
slave devices such as the DS18B20 sensor, and for offloading CPU cycles from
the main processor.

A Bus Pirate (http://dangerousprototypes.com/docs/Bus_Pirate) was used as a
convenient bridge between a PC and the I2C bus. Since the Bus Pirate layer will
not be present in an embedded solution, that layer and its required interface
handshaking is hidden away in the bus_pirate.py module. The code specific
to talking to the 1-Wire temperature sensors via the I2C to 1-Wire bridge is
all in the test_ds18b20.py file.

Note: The Bus Pirate can be used via a command line interface to talk directly
to 1-Wire devices, and that facility was used to obtain the unique 1-Wire
addresses of the sensors. There was little point in prototyping the quite
complex search algorithm because that is already available in 'C' language form
from Dallas Semiconductor (Application Note 187, 1-Wire Search Algorithm).

    Below is output from the BusPirate using Macro 240 in 1-Wire mode, showing
    the 2 discovered devices and their 1-Wire addresses:

        1-WIRE>(240)
        SEARCH (0xF0)
        Macro     1WIRE address
         1.0x28 0xA9 0xE8 0x83 0x06 0x00 0x00 0xB0
           *DS18B20 Prog Res Dig Therm
         2.0x28 0x23 0x49 0x83 0x06 0x00 0x00 0x6B
           *DS18B20 Prog Res Dig Therm

Here is some example output from the program, intended to help rewriting the
algorithms in 'C' or 'C++' for use with an MCU (in my case the intended target
is an STI ARM Cortex MCU).

Note: The 2 devices were patched on a breadboard just touching one another.
The measured temperatures were:
   temp C = 20.25
   temp C = 20.0625
Which also provided me some confidence in the devices stated accuracy.

C:\Python34\python.exe W:/GitHub/BusPirate/DS18C20/test_ds18b20.py
BusPirate init
  BusPirate : reset
    >> 0f
  BusPirate : binary mode
    >> 00
      << 42 42 49 4f 31
  BusPirate : I2C mode
    >> 02
      << 49 32 43 31
  BusPirate : set I2C peripherals
    >> 4c
  BusPirate : set I2C speed
    >> 62
DS2484 init
I2cWriteCommand : DS2484 reset
  { -- i2c transaction --
    >> 30 f0
  }
DS18B20 init
I2cWriteCommand : DS2484 write config
  { -- i2c transaction --
    >> 30 d2 e1
  }
Measure temperature.
  Send OW : DS18B20 measure temperature
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 08
  }
DS2484 Status = LL^
I2cWriteCommand : DS2484 reset OW
  { -- i2c transaction --
    >> 30 b4
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 55
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 28
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 23
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 49
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 83
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 06
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 6b
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 44
  }
Get temperature from DS18B20 device id=[ 28 23 49 83 06 00 00 6b ]
  Read OW : DS18B20 read scratch pad
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 reset OW
  { -- i2c transaction --
    >> 30 b4
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 55
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 28
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 23
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 49
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 83
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 06
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 6b
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 be
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 read 8 OW bits into data register
  { -- i2c transaction --
    >> 30 96
  }
  { -- i2c transaction --
    >> 30 e1 e1
  }
I2cReadCommand : DS2484 read data register
  { -- i2c transaction --
    >> 30 e1 e1
  }
  { -- i2c transaction --
    >> 31
      << 44
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 read 8 OW bits into data register
  { -- i2c transaction --
    >> 30 96
  }
  { -- i2c transaction --
    >> 30 e1 e1
  }
I2cReadCommand : DS2484 read data register
  { -- i2c transaction --
    >> 30 e1 e1
  }
  { -- i2c transaction --
    >> 31
      << 01
  }
temp C = 20.25
temp F = 68.45
Measure temperature.
  Send OW : DS18B20 measure temperature
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 reset OW
  { -- i2c transaction --
    >> 30 b4
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 55
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 28
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 a9
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 e8
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 83
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 06
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 b0
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 44
  }
Get temperature from DS18B20 device id=[ 28 a9 e8 83 06 00 00 b0 ]
  Read OW : DS18B20 read scratch pad
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 reset OW
  { -- i2c transaction --
    >> 30 b4
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 55
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 28
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 a9
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 e8
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 83
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 06
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 00
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 b0
  }
I2cWriteCommand : DS2484 send OW write byte
  { -- i2c transaction --
    >> 30 a5 be
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 read 8 OW bits into data register
  { -- i2c transaction --
    >> 30 96
  }
  { -- i2c transaction --
    >> 30 e1 e1
  }
I2cReadCommand : DS2484 read data register
  { -- i2c transaction --
    >> 30 e1 e1
  }
  { -- i2c transaction --
    >> 31
      << 41
  }
ow_wait_until_idle
read status
  { -- i2c transaction --
    >> 30 e1 f0
  }
I2cReadCommand : DS2484 read status register
  { -- i2c transaction --
    >> 30 e1 f0
  }
  { -- i2c transaction --
    >> 31
      << 0a
  }
DS2484 Status = LL^ PPD
I2cWriteCommand : DS2484 read 8 OW bits into data register
  { -- i2c transaction --
    >> 30 96
  }
  { -- i2c transaction --
    >> 30 e1 e1
  }
I2cReadCommand : DS2484 read data register
  { -- i2c transaction --
    >> 30 e1 e1
  }
  { -- i2c transaction --
    >> 31
      << 01
  }
temp C = 20.0625
temp F = 68.11250000000001
Done
*** BusPirate Cleanup ***
  BusPirate : reset
    >> 0f
  BusPirate : UART mode
    >> 03

Process finished with exit code 0
