"""
 *  NOTE      - sht31.py
 *  Author    - Ista
 *
 *  Created   - 2022.11.18
 *  Github    - https://github.com/vine91
 *  Contact   - vine9151@gmail.com
"""

from pyftdi.i2c import I2cController, I2cNackError
import time


class Sht31:
  """ Class of SHT31 temperature & humidity sensor. """

  def __init__(self, device='ftdi:///?'):
    self.i2c = I2cController()
    self.i2c.configure(device)
    self.init_i2c()

  def init_i2c(self):
    """ Function to init i2c slave """

    self.selected_slave = int(input("type the slave address (hex): "), 16)
    self.slave = self.i2c.get_port(self.selected_slave)

    # Send one byte, then receive one byte
    self.slave.exchange([0x04], 1)

    # Write a register to the I2C slave
    #self.slave.write_to(0x06, b'\x00')

    # Read a register from the I2C slave
    self.slave.read_from(0x00, 1)

  def raw_temp_humi(self):
    """
    Read the raw temperature and humidity from the sensor and skips CRC
    checking.
    Returns a tuple for both values in that order.
    """

    self.slave.write_to(0x2c, b'\x06')
    time.sleep(0.05)
    raw = self.slave.read_from(self.selected_slave, 6)

    return (raw[0] << 8) + raw[1], (raw[3] << 8) + raw[4]

  def get_temp_humi(self, celsius=True):
    """
    Read the temperature in degree celsius or fahrenheit and relative
    humidity. Resolution and clock stretching can be specified.
    Returns a tuple for both values in that order.
    """

    t, h = self.raw_temp_humi()
    if celsius:
      temperature = -45 + (175 * (t / 65535))
    else:
      temperature = -49 + (315 * (t / 65535))
    humidity = 100 * (h / 65535)

    return temperature, humidity

  def start_loop(self):
    """ Function to start sensor """

    print("\n")

    time.sleep(1)
    t, h = self.get_temp_humi()

    if h <= 2:
      self.temp, self.humi = round(t, 2), round(h, 2)
    else:
      self.temp, self.humi = round((t/100) * 90, 2), round((h/100) * 90, 2)

    #self.temp, self.humi = round(t, 2), round(h, 2)

    print("temp: {0}".format(self.temp))
    print("humi: {0}\n".format(self.humi))

  def end_loop(self):
    """ Function to End Loop """

    self.i2c.terminate()

  def get_temperature(self):
    """ Function to Get Temperature """

    return self.temp

  def get_humidity(self):
    """ Function to Get Humidity """

    return self.humi
