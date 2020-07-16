
import lirc

# for this to work kill the lircd service: sudo /etc/init.d/lircd stop and start it manually: lircd --nodaemon

class LIRC:
    def __init__(self):
        self.sock = lirc.init("myprog", blocking=False)

    def key_pressed(self):
        key = None
        key = lirc.nextcode()
        if key is None:
            return False
        if len(key) == 0:
            return False
        return True
