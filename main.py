
from scan import Scan
from drive import Driver
from proximity import Proximity
import pigpio
import settings

class MainApp:
    def __init__(self):
        self.piconn = pigpio.pi()
        if not self.piconn.connected:
            print('failed to connect to pigpio deamon - start it')
            exit()
        self.proximity = Proximity(self.piconn)
        self.driver = Driver(self.piconn, self.proximity)
        self.scanner = Scan(self.piconn)

    def run(self):
        while True:
            found, mode, width, x = self.scanner.scan()
            if found == True:
                chase = self.rotate_to_center(mode, width, x)
                if chase == True:
                    self.driver.chase(settings.CHASE_DURATION)

        del scanner
        piconn.stop()

    def rotate_to_center(self, mode, width, x):
        idata = settings.imagedata[mode]
        print (idata)
        xsector = int(x / idata['sector_width'])
        durationx = 0
        durationw = 0
        midsector = idata['mid_sector']
        if xsector > midsector:
            durationx = (xsector - midsector) * settings.MOVEMENT_DURATION
        elif xsector < midsector:
            durationx = (midsector - xsector) * settings.MOVEMENT_DURATION * -1
        if width < settings.CENTER_WIDTH:
            durationw = (int((settings.CENTER_WIDTH - width) / 50)) * settings.MOVEMENT_DURATION
        elif width > settings.CENTER_WIDTH:
            durationw = (int((width - settings.CENTER_WIDTH) / 50)) * settings.MOVEMENT_DURATION * -1

        duration = durationx + durationw
        print ('xsector: {} durationx: {}  width: {} durationw: {}  duration: {}'.format(xsector, durationx, width, durationw, duration))

        if duration > 0:
            self.driver.rotateright(duration)
        else:
            self.driver.rotateleft(duration * -1)

        # check if the car is already pointing to the target. If yet, then chase.
        if durationx == 0 and durationw == 0:
            return True

        return False

def main():
    mainapp = MainApp()
    mainapp.run()

if __name__ == "__main__":
    main()

