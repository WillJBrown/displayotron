import time
import subprocess
from mypylib import screen
from sys import exit

from dot3k.menu import MenuOption

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
    return output

class SysShutdown(MenuOption):
    """Shuts down the Raspberry Pi"""

    def __init__(self):
        self.last = self.millis()
        MenuOption.__init__(self)

    def redraw(self, menu):
        shutdown = "shutdown -h now"

        now = self.millis()
        if now - self.last < 1000 * 5:
            return False

        menu.write_row(0, 'RPI Shutdown')
        menu.write_row(1, '')
        menu.write_row(2, time.strftime('  %a %H:%M:%S  '))

        time.sleep(2)
        screen.off()

        a = run_cmd(shutdown)

class SysReboot(MenuOption):
    """Reboots the Raspberry Pi"""

    def __init__(self):
        self.last = self.millis()
        MenuOption.__init__(self)

    def redraw(self, menu):
        reboot = "reboot"

        now = self.millis()
        if now - self.last < 1000 * 5:
            return False

        menu.write_row(0, 'RPI Reboot')
        menu.write_row(1, '')
        menu.write_row(2, time.strftime('  %a %H:%M:%S  '))

        time.sleep(2)
        screen.off()

        a = run_cmd(reboot)

class Exit(MenuOption):
    """
    This exits the menu program
    """

    def __init__(self):
        self.last = self.millis()
        MenuOption.__init__(self)

    def redraw(self, menu):
        now = self.millis()
        if now - self.last < 1000 * 5:
            return False
        sys.exit()

