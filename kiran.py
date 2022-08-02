import dmx

from kivy.app import App
from kivy.lang import Builder

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem

from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.tabbedpanel import TabbedPanel

channels = ['master','red','green','blue','white']
channelColors = [[1,1,1,255],[1,0,0,255],[0,1,0,255],[0,0,1,255],[1,1,1,255]]

class Channel:
  def __init__(self, address, color):
    self.color = color
    self.address = address
    self.slider = Slider(min=0, max=255,value=0,orientation='vertical',value_track=True, size_hint=(1,20))
    self.addrLabel = Label(text=str(address))
    self.typeLabel = Label(text=str(color))
    self.value = Label(text='0')
    self.slider.bind(value=self.onSliderChange)
    self.value.bind(text=self.valueInputChange)

  def onSliderChange(self, instance, brightness):
    self.value.text = str(int(brightness))
    trackValue = brightness/255
    colorFrame = channelColors[channels.index(self.color)]
    colorFrame = [i*brightness/255 for i in colorFrame]
    self.slider.value_track_color=colorFrame
    universe.setChannelValue(self.address, brightness)
    universe.render()

  def valueInputChange(self, instance, brightness):
    self.value.text=str(brightness)
    self.slider.value=self.getValue(brightness)

  def getValue(self, text):
    if int(text) <= 255 or int(text) >= 0:
      return int(text)
    else:
      return 0

class ChannelGroup:
  def __init__(self, addresses, color, name=""):
    self.color = color
    self.addresses = addresses
    self.slider = Slider(min=0, max=255,value=0,orientation='vertical',value_track=True, size_hint=(1,20))
    self.addrLabel = Label(text=str(addresses))
    self.typeLabel = Label(text=color)
    self.value = Label(text='0')
    self.slider.bind(value=self.onSliderChange)
    self.value.bind(text=self.valueInputChange)

  def onSliderChange(self, instance, brightness):
    self.value.text = str(int(brightness))
    trackValue = brightness/255
    colorFrame = channelColors[channels.index(self.color)]
    colorFrame = [i*brightness/255 for i in colorFrame]
    self.slider.value_track_color=colorFrame
    universe.setChannelsValue(self.addresses, brightness)
    universe.render()

  def valueInputChange(self, instance, brightness):
    self.value.text=str(brightness)
    self.slider.value=self.getValue(brightness)

  def getValue(self, text):
    if int(text) <= 255 or int(text) >= 0:
      return int(text)
    else:
      return 0

class Fixture:

  def __init__(self, channels):

    self.channels = channels

    self.window = BoxLayout(orientation='horizontal')
    self.channelWindows = []

    for channel in self.channels:
      channelWindow = BoxLayout(orientation='vertical')
      channelWindow.add_widget(channel.slider)
      channelWindow.add_widget(channel.value)
      channelWindow.add_widget(channel.addrLabel)
      channelWindow.add_widget(channel.typeLabel)
      self.channelWindows.append(channelWindow)

    for channelWindow in self.channelWindows:
      self.window.add_widget(channelWindow)

class GroupPanel:
  def __init__(self, group):
    self.root = group
    self.name = self.root.name
    # Create a box layout
    self.window = BoxLayout()

    self.cgs = []
    self.channelWindows = []

    for channelGroup, channels in self.root.channelGroups.items():
      # Create a channel group object for each channel group
      name = self.root.channelGroupNames[channelGroup]
      self.cgs.append(ChannelGroup(channels, channelGroup, name))
      cg = self.cgs[-1]
      # Create a window for each channel group
      channelWindow = BoxLayout(orientation='vertical')
      # Create a slider for each channel group
      channelWindow.add_widget(cg.slider)
      channelWindow.add_widget(cg.value)
      channelWindow.add_widget(cg.addrLabel)
      channelWindow.add_widget(cg.typeLabel)
      self.channelWindows.append(channelWindow)

    for channelWindow in self.channelWindows:
      self.window.add_widget(channelWindow)

class AksharKiran(App):
  def build(self):

    self.window = BoxLayout(orientation='vertical')

    self.tabs = TabbedPanel(do_default_tab=False)

    self.groupPanels = []
    for group in universe.groups:
      self.groupPanels.append(GroupPanel(group))

    self.fixtures = []
    for fixture in universe.fixtures:
      channelSliders = []
      for channelType, channelAddress in fixture.channels.items():
        print("Channel address of", channelType, "is:", channelAddress)
        channelSlider = Channel(channelAddress, channelType)
        channelSliders.append(channelSlider)
      self.fixtures.append(Fixture(channelSliders))

    self.logo = Image(source='text.png', size_hint=(1,0.1))

    self.window.add_widget(self.logo)


    for index, group in enumerate(self.groupPanels):
      tab = TabbedPanelItem(text=group.name)
      tab.add_widget(group.window)
      self.tabs.add_widget(tab)

    for index, fixture in enumerate(self.fixtures):
      tab = TabbedPanelItem(text='Fixture {}'.format(index+1))
      tab.add_widget(fixture.window)
      self.tabs.add_widget(tab)

    # for tab in self.tabs:
    #   self.window.add_widget(tab)

    self.window.add_widget(self.tabs)

    return self.window

if __name__ == '__main__':
  universe = dmx.Universe()
  AksharKiran().run()
