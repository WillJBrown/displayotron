from dot3k.menu import Menu, MenuOption

class Blank(MenuOption):

    def __init__(self, backlight=None, lcd=None):
        self.last = self.millis()
        if backlight is None:
            import dothat.backlight
            self.backlight = dothat.backlight
        else:
            self.backlight = backlight
        if lcd is None:
            import dothat.lcd
            self.lcd = dothat.lcd
        else:
            self.lcd = lcd
        self.leds = [0x00] * 18
        self.blankstring = '                '
        self.contrast=40
        MenuOption.__init__(self)

    def setup(self, config):
        self.config = config
        self.contrast = int(self.get_option('Display', 'contrast', 50))

    def begin(self):
        self.can_idle = True
        if self.idling:
            self.leds = self.backlight.leds
            self.backlight.off()
            self.backlight.set_graph(0)
            self.lcd.set_contrast(0)

    def redraw(self, menu):
        now = self.millis()
        if now - self.last < 1000:
            return False
        for line in range(3):
            menu.write_row(line, self.blankstring)


    def cleanup(self):
        if self.idling:
            self.lcd.set_contrast(self.contrast)
            self.backlight.leds = self.leds
            self.backlight.update()
