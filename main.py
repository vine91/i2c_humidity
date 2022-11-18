"""
 *  NOTE      - main.py
 *  Author    - Ista
 *
 *  Created   - 2022.11.17
 *  Github    - https://github.com/vine91
 *  Contact   - vine9151@gmail.com
"""

from src.i2c_scan import I2CScan, Ftdi, FtdiLogger, ArgumentParser, FileType, Formatter, StreamHandler, add_custom_devices, DEBUG, ERROR
from src.sht31 import Sht31
from sys import modules, stderr
import time, traceback, sys


if __name__ == '__main__':
  """Entry point."""
  debug = False
  try:
    argparser = ArgumentParser(description=modules[__name__].__doc__)
    argparser.add_argument('device', nargs='?', default='ftdi:///?',  help='serial port device name')
    argparser.add_argument('-S', '--no-smb',    action='store_true',  default=False, help='use regular I2C mode vs. SMBbus scan')
    argparser.add_argument('-P', '--vidpid',    action='append',      help='specify a custom VID:PID device ID, may be repeated')
    argparser.add_argument('-V', '--virtual',   type=FileType('r'),   help='use a virtual device, specified as YaML')
    argparser.add_argument('-v', '--verbose',   action='count',       default=0, help='increase verbosity')
    argparser.add_argument('-d', '--debug',     action='store_true',  help='enable debug mode')
    args = argparser.parse_args()
    debug = args.debug

    if not args.device:
      argparser.error('Serial device not specified')

    loglevel = max(DEBUG, ERROR - (10 * args.verbose))
    loglevel = min(ERROR, loglevel)
    if debug:
      formatter = Formatter('%(asctime)s.%(msecs)03d %(name)-20s %(message)s', '%H:%M:%S')
    else:
      formatter = Formatter('%(message)s')
    FtdiLogger.log.addHandler(StreamHandler(stderr))
    FtdiLogger.set_formatter(formatter)
    FtdiLogger.set_level(loglevel)

    if args.virtual:
      from pyftdi.usbtools import UsbTools
      # Force PyUSB to use PyFtdi test framework for USB backends
      UsbTools.BACKENDS = ('pyftdi.tests.backend.usbvirt', )
      # Ensure the virtual backend can be found and is loaded
      backend = UsbTools.find_backend()
      loader = backend.create_loader()()
      loader.load(args.virtual)

    try:
      add_custom_devices(Ftdi, args.vidpid, force_hex=True)
    except ValueError as exc:
      argparser.error(str(exc))

    I2CScan.scan(args.device, not args.no_smb)

  except (ImportError, IOError, NotImplementedError, ValueError) as exc:
    print('\nError: %s' % exc, file=stderr)
    if debug:
        print(format_exc(chain=False), file=stderr)
    exit(1)
  except KeyboardInterrupt:
    exit(2) 

  except Exception:
    print(traceback.format_exc())
    print(sys.exc_info()[2])

  else:
    time.sleep(1)
    sht31 = Sht31(args.device)
    sht31.start()
