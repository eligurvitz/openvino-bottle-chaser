
import pigpio
import time

TRIG = 23
ECHO = 24
REASONABLE_DELTA = 30

class Proximity:
    def __init__(self, piconn):
        self.pi = piconn
        print("Waiting For proximity sensor To settle")
        self.pi.set_mode(TRIG, pigpio.OUTPUT)
        self.pi.set_mode(ECHO, pigpio.INPUT)
        self.pi.write(TRIG, 0)
        time.sleep(1)
        self.previous = -1
        return

    def __del__(self):
        return

    def measure(self):
        pulse_start = 0
        pulse_end = 0

        self.pi.write(TRIG, 1)
        time.sleep(0.00001)
        self.pi.write(TRIG, 0)
        while self.pi.read(ECHO) == 0:
            pulse_start = time.time()
        while self.pi.read(ECHO) == 1:
            pulse_end = time.time()

        if pulse_start == 0 or pulse_end == 0:
            distance = -1
            print("invalid distance reading")
        else:
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)

        print ("Distance: {} cm".format(distance))
        return distance