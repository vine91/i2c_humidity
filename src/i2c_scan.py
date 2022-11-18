"""
 *  NOTE      - i2c_scan.py
 *  Author    - Ista
 *
 *  Created   - 2022.11.17
 *  Github    - https://github.com/vine91
 *  Contact   - vine9151@gmail.com
"""

from argparse import ArgumentParser, FileType
from logging import Formatter, StreamHandler, getLogger, DEBUG, ERROR
from sys import modules, stderr
from traceback import format_exc
from pyftdi import FtdiLogger
from pyftdi.ftdi import Ftdi
from pyftdi.i2c import I2cController, I2cNackError
from pyftdi.misc import add_custom_devices
import numpy as np


class I2CScan:
  """Scan I2C bus to find slave.
     Emit the I2C address message, but no data. Detect any ACK on each valid
     address.
  """

  SMB_READ_RANGE = list(range(0x30, 0x38)) + list(range(0x50, 0x60))

  HIGHEST_I2C_SLAVE_ADDRESS = 0x78

  @classmethod
  def scan(cls, url: str, smb_mode: bool = True) -> None:
    """Scan an I2C bus to detect slave device.
       :param url: FTDI URL
       :param smb_mode: whether to use SMBbus restrictions or regular I2C
                        mode.
    """
    i2c = I2cController()
    slaves = []
    getLogger('pyftdi.i2c').setLevel(ERROR)
    try:
      i2c.set_retry_count(1)
      i2c.configure(url)
      for addr in range(cls.HIGHEST_I2C_SLAVE_ADDRESS+1):
        port = i2c.get_port(addr)
        if smb_mode:
          try:
            if addr in cls.SMB_READ_RANGE:
              port.read(0)
              slaves.append('R')
            else:
              port.write([])
              slaves.append('W')
          except I2cNackError:
              slaves.append('.')
        else:
          try:
            port.read(0)
            slaves.append('R')
            continue
          except I2cNackError:
            pass
          try:
            port.write([])
            slaves.append('W')
          except I2cNackError:
            slaves.append('.')
    finally:
      i2c.terminate()
    columns = 16
    row = 0
    print('   %s' % ''.join(' %01X ' % col for col in range(columns)))
    while True:
      chunk = slaves[row:row+columns]
      if not chunk:
        break
      print(' %1X:' % (row//columns), '  '.join(chunk))
      row += columns

    cls.get_addr(slaves)

  def get_addr(scaned_list):
    """ Function to get address. """

    scaned_numpy = np.array(scaned_list)
    slave_addr = np.where(scaned_numpy == 'W')[0]

    for key, value in enumerate(slave_addr):
      tens_digit = 0
      unit_digit = value % 16

      if value >= 16:
        tens_digit = round(value / 16)

      print("activated slave address {0}: {1}".format(key, hex((tens_digit * 16) + unit_digit)))
