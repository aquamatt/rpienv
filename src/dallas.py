#
# Read the Dallas DS18b20 digital temperature sensors via the RPi 1-wire
# device interface.
#
# Example output from the device:
#
# 97 01 55 00 7f ff 0c 10 de : crc=de YES
# 97 01 55 00 7f ff 0c 10 de t=25437
import sys


WIRE_ROOT = "/sys/bus/w1/devices"


def read_temperature(device_id):
    try:
        with open("{}/{}/w1_slave"
                  .format(WIRE_ROOT, device_id), "rt") as sensor:
            lines = sensor.readlines()
            temp = int(lines[1].split()[-1][2:].strip()) / 1000.0
            return temp
    except IOError:
        # a semi silent fail here...
        sys.stderr.write("Could not read Dallas device {}\n".format(device_id))
        sys.stderr.flush()
        return None
