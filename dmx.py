# || Swami-Shriji ||

#--------------------#
#      Libraries     #
#--------------------#
import numpy as np
import serial
import serial.tools.list_ports
import sys
from lxml import etree as et

#--------------------#
#       Classes      #
#--------------------#

class Message:

  __startByte = 0x7E
  __outputOnlySendDMX = 0x06
  __endByte = 0xE7

  def __init__(self, frame):
    self.frame = frame.tolist()

  def getBinary(self):
    binaryMsg = [self.__startByte, self.__outputOnlySendDMX]
    binaryMsg.extend(bytearray([
      (len(self.frame) + 1) & 0xFF, # LSB of data length
      ((len(self.frame) + 1) >> 8) & 0xFF, # MSB of data length (2 bytes max)
    ]))
    binaryMsg.extend(self.frame)
    binaryMsg.append(self.__endByte)
    return bytearray(binaryMsg)

  
#--------------------#
#       Classes      #
#--------------------#

# A Universe class controls a 512 byte frame, aka a DMX Universe.
class Universe:

  # Open a serial port using pyserial
  def __openSerialPort(self):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
      if "SparkFun" in p.description:
          serDevice = p.device
          print(serDevice)
    try:
        ser = serial.Serial(serDevice, baudrate=57600, dsrdtr=True, timeout=3)
        print(ser)
    except:
        print("Unable to find DMX device.")
        sys.exit(1)

    print("DMX device found at " + serDevice + ".")
    self.ser = ser

  # Get fixtures from an xml file
  def __getFixtures(self, dmxCfgFile='fixtures.xml'):
    tree = et.parse(dmxCfgFile)
    root = tree.getroot()
    self.fixtures = []
    fixtureElements = root.findall('fixture')
    for element in fixtureElements:
      self.fixtures.append(Fixture(element))

  # Get groups from an xml file
  def __getGroups(self, dmxCfgFile='fixtures.xml'):
    tree = et.parse(dmxCfgFile)
    root = tree.getroot()
    self.groups = []
    groupElements = root.findall('group')
    for element in groupElements:
      self.groups.append(Group(element))

  # Constructor
  def __init__(self, port='dev/ttyUSB0'):
    self.frame = np.zeros(512, dtype='u8')
    self.__openSerialPort()
    self.__getFixtures()
    self.__getGroups()

  # Write frame to serial port
  def render(self):
    self.ser.write(self.frame.tolist())
    print(Message(self.frame).getBinary())

  # Set the value of a single channel
  def setChannelValue(self, address, value):
    self.frame[address] = value

  # Set the value of multiple channels
  def setChannelsValue(self, addresses, value):
    for address in addresses:
      self.frame[address] = value

# The Fixture class represents an xml defined fixture (group of channels)
class Fixture:

  def __init__(self, xml_element):
    self.name = xml_element.get('name')
    self.address = int(xml_element.get('address'))
    self.channels = {}
    for element in xml_element.getchildren():
      typeOfChannel = element.get('type')
      relative_address = int(element.get('relative_address'))
      self.channels[typeOfChannel] = self.address + relative_address

# A Group is similar to a fixture, only that all the channels in a group are of the same channel type
class Group:

  def __init__(self, xml_element):
    self.name = xml_element.get('name')
    self.channelGroups = {}
    self.channelGroupNames = {}
    for channelGroup in xml_element.findall('channel_group'):
      typeOfChannelGroup = channelGroup.get('type')
      self.channelGroupNames.update({typeOfChannelGroup:channelGroup.get('name')})
      self.channelGroups[typeOfChannelGroup] = []
      for channel in channelGroup.findall('channel'):
        self.channelGroups[typeOfChannelGroup].append(int(channel.get('address')))

    print(self.channelGroupNames)

# TODO: remove
class DMX:

  def __init__(self, dmxCfgFile):
    tree = et.parse(dmxCfgFile)
    root = tree.getroot()
    self.fixtures = []
    for element in root:
      self.fixtures.append(Fixture(element))
      
      
if __name__ == "__main__":
  a = DMX('fixtures.xml')
