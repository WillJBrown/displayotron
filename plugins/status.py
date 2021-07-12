import subprocess
import time
import psutil
from mypylib import rpi

from dot3k.menu import Menu, MenuOption


def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
    return output


def get_current_down(iface='wlan0'):
    show_dl_raw = "ifconfig " + iface + " | grep bytes | grep RX | cut -d' ' -f14"
    raw_dl = run_cmd(show_dl_raw)
    return raw_dl


def get_current_up(iface='wlan0'):
    show_ul_raw = "ifconfig " + iface + " | grep bytes | grep TX | cut -d' ' -f14"
    raw_ul = run_cmd(show_ul_raw)
    return raw_ul


class Status(MenuOption):

    def __init__(self, backlight=None):
        self.last = self.millis()
        if backlight is None:
            import dothat.backlight
            self.backlight = dothat.backlight
        else:
            self.backlight = backlight
        self.samplecount = 0
        self.refreshrate = 1
        self.leds = [0x00] * 18
        self.cpu_samples = [0] * 20
        self.cputemp_samples = [0] * 10
        self.gputemp_samples = [0] * 10
        self.raw_dlold = 0
        self.raw_ulold = 0
        self.dlspeed = 0
        self.ulspeed = 0
        self.iface = 'wlan0'
        self.is_setup = False
        MenuOption.__init__(self)

    def begin(self):
        self.can_idle = True
        if self.idling:
            self.samplecount = 0
            self.refreshrate = 10
            self.leds = self.backlight.leds
            self.backlight.off()
            self.backlight.set_graph(0)

    def redraw(self, menu):
        tdelta = self.millis() - self.last
        if self.samplecount > 20 and tdelta < self.refreshrate * 1000:
            return False
        self.last = self.millis()

        if not self.is_setup:
            self.samplecount = 0
            menu.lcd.create_char(0, [0, 0, 4, 14, 31, 0, 0, 0])  # Up arrow
            menu.lcd.create_char(1, [0, 0, 0, 31, 14, 4, 0, 0])  # Down arrow
            menu.lcd.create_char(2, [0, 14, 17, 4, 10, 0, 4, 0])  # WiFi
            menu.lcd.create_char(3, [0, 0, 31, 17, 17, 14, 0, 0])  # Ethernet
            menu.lcd.create_char(4, [0, 4, 6, 7, 6, 4, 0, 0])  # Right Arrow
            menu.lcd.create_char(5, [0, 4, 12, 28, 12, 4, 0, 0])  # Left Arrow

            self.is_setup = True

        if self.samplecount <= 20:
            #print('Samples: ' + str(self.samplecount))
            self.samplecount += 1

        self.cpu_samples.append(psutil.cpu_percent())
        self.cpu_samples.pop(0)
        cpu_avg = round(sum(self.cpu_samples) / len(self.cpu_samples))

        self.cputemp_samples.append(rpi.getcputemp())
        self.cputemp_samples.pop(0)
        cputemp = round(sum(self.cputemp_samples) / len(self.cputemp_samples))
        self.gputemp_samples.append(rpi.getgputemp())
        self.gputemp_samples.pop(0)
        gputemp = round(sum(self.gputemp_samples) / len(self.gputemp_samples))
        temp = max(cputemp, gputemp)
        cpu = (cputemp >= gputemp)
        if cpu:
            source = 'CPU'
        else:
            source = 'GPU'

        raw_dlnew = get_current_down(self.iface)
        raw_ulnew = get_current_up(self.iface)

        self.dlspeed = 0
        self.ulspeed = 0

        try:
            ddelta = int(raw_dlnew) - int(self.raw_dlold)
            udelta = int(raw_ulnew) - int(self.raw_ulold)

            self.dlspeed = float(ddelta) / float(tdelta)
            self.ulspeed = float(udelta) / float(tdelta)
        except ValueError:
            pass

        self.raw_dlold = raw_dlnew
        self.raw_ulold = raw_ulnew

        up_mb: float = round(8 * self.ulspeed / 1024, 1)
        down_mb: float = round(8 * self.dlspeed / 1024, 1)

        bottomline = chr(2) + '{:>4}'.format(down_mb) + 'Mb' + chr(1) + '{:>4}'.format(up_mb) + 'Mb' + chr(0) + chr(4)
        if self.iface != 'wlan0':
            bottomline = chr(5) + '{:>4}'.format(down_mb) + 'Mb' + chr(1) + '{:>4}'.format(up_mb) +\
                         'Mb' + chr(0) + chr(3)

        menu.write_row(0, 'Load ' + str(cpu_avg) + '% ' + str(source) + ' ' + str(temp)[:2] + "C")
        timestring = '   %a %H:%M   '
        if not self.idling:
            timestring = '  %a %H:%M:%S  '
        menu.write_row(1, time.strftime(timestring))
        menu.write_row(2, bottomline)

    def cleanup(self):
        if self.idling:
            self.backlight.leds = self.leds
            self.backlight.update()
            self.refreshrate = 1
        self.is_setup = False

    def right(self):
        self.iface = 'eth0'
        return True

    def left(self):
        self.iface = 'wlan0'
        return True
