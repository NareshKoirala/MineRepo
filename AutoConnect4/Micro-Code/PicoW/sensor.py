from machine import Pin

def sensor_init(pins: list) -> list:
    sensor_pin = []
    for i in pins:
        sensor_pin.append(Pin(i, Pin.IN))
    return sensor_pin

def sensor_irq(ls_pins: list, func):
    for pins in ls_pins:
        pins.irq(trigger=Pin.IRQ_FALLING, handler=func)