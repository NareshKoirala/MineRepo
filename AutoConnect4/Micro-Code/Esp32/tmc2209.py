from machine import Pin
import utime

step_pin = None
dir_pin = None
enable_pin = None
solenoid_pin_1 = None
solenoid_pin_2 = None

move_val = 1397

def tmc_init (step_p : int, dir_p : int, enable_p : int, sole_1 : int, sole_2 : int) :
    global step_pin, dir_pin, enable_pin, solenoid_pin_1, solenoid_pin_2

    step_pin = Pin(step_p, Pin.OUT)   # STEP
    dir_pin = Pin(dir_p, Pin.OUT)    # DIR
    enable_pin = Pin(enable_p, Pin.OUT) # EN    

    solenoid_pin_1 = Pin(sole_1, Pin.OUT)
    solenoid_pin_2 = Pin(sole_2, Pin.OUT)

    enable_pin.value(0)

def step_motor(steps, direction, delay_ms=2):
    
    global step_pin, dir_pin, enable_pin, move_val

    dir_pin.value(direction)  # 0 or 1 to set direction

    for _ in range(steps * move_val):
        step_pin.value(1)     # Pulse high
        utime.sleep_ms(delay_ms // 2)  # Half delay
        step_pin.value(0)     # Pulse low
        utime.sleep_ms(delay_ms // 2)  # Half delay

# hopper
def solenoid(enab : int):
    global solenoid_pin_1

    solenoid_pin_1.value(enab)

# cyclinder
def solenoid_1(enab : int):
    global solenoid_pin_2

    solenoid_pin_2.value(enab)