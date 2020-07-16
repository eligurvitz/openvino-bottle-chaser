import time
import pigpio
import proximity
import settings

ENA = 16
ENB = 26
PIN1 = 12
PIN2 = 13
PIN3 = 6
PIN4 = 5
WIDTH = 1000

class Driver:
    def __init__(self, piconn, proximity):
        self.pi = piconn
        self.prox = proximity
        return

    def __del__(self):
        return

    def stop(self):
        self.pi.write(PIN1, 0)
        self.pi.write(PIN2, 0)
        self.pi.write(PIN3, 0)
        self.pi.write(PIN4, 0)
        self.pi.write(ENA, 0)
        self.pi.write(ENB, 0)
        return

    def rotateright(self, duration):
        self.pi.write(ENA, 1)
        self.pi.write(ENB, 1)
        self.pi.write(PIN1, 1)
        self.pi.write(PIN2, 0)
        self.pi.write(PIN3, 1)
        self.pi.write(PIN4, 0)
        time.sleep(duration)
        self.stop()

        return

    def rotateleft(self, duration):
        self.pi.write(ENA, 1)
        self.pi.write(ENB, 1)
        self.pi.write(PIN1, 0)
        self.pi.write(PIN2, 1)
        self.pi.write(PIN3, 0)
        self.pi.write(PIN4, 1)
        time.sleep(duration)
        self.stop()
        return

    def forward(self, duration):
        self.pi.write(ENA, 1)
        self.pi.write(ENB, 1)
        self.pi.write(PIN1, 1)
        self.pi.write(PIN2, 0)
        self.pi.write(PIN3, 0)
        self.pi.write(PIN4, 1)
        time.sleep(duration)
        self.stop()
        return

    def backward(self, duration):
        self.pi.write(ENA, 1)
        self.pi.write(ENB, 1)
        self.pi.write(PIN1, 0)
        self.pi.write(PIN2, 1)
        self.pi.write(PIN3, 1)
        self.pi.write(PIN4, 0)
        time.sleep(duration)
        self.stop()
        return

    def chase(self, duration):
        interval = 0

        self.pi.write(ENA, 1)
        self.pi.write(ENB, 1)

        distance = self.prox.measure()
        print('chasing - distance = {}'.format(distance))
        while distance > settings.MIN_CHASE_DISTANCE and distance < settings.MAX_CHASE_DISTANCE and interval < settings.CHASE_INTERVALS:
            print('chasing - distance = {}'.format(distance))
            self.pi.write(PIN1, 1)
            self.pi.write(PIN2, 0)
            self.pi.write(PIN3, 0)
            self.pi.write(PIN4, 1)
            time.sleep(duration / settings.CHASE_INTERVALS)
            interval = interval + 1
            distance = self.prox.measure()
        self.stop()
