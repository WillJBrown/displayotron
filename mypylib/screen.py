from dothat import backlight
from dothat import lcd

def off():
    backlight.off()
    lcd.set_contrast(0)
    lcd.clear()

def start():
    backlight.off()
    lcd.clear()
    lcd.set_contrast(52)
