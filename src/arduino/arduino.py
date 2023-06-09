import serial
import serial.tools.list_ports
import time


class Arduino:
    def __init__(self, p="COM14"):
        self.port = p
        self.port_OK = False
        self.open_port()
        if not self.port_OK:
            for p in self.get_ports():
                self.port = p
                self.open_port()
                if self.port_OK:
                    break
            if not self.port_OK:
                raise Exception("No Arduino ?")

    def write(self, x):
        """
        Send message to Arduino board.
        """
        self.board.write(bytes(x + "\n", "utf-8"))

    def close(self):
        """
        Close Arduino board.
        """
        self.board.close()

    def check_port(self):
        """
        Check if Arduino board is present and with correct program.
        """
        self.write("v")
        r = self.board.readline()
        st = r.decode("utf-8")
        if len(r) > 0:
            if st.strip() == "ok":  # reply
                self.port_OK = True
            else:
                self.port_OK = False
        else:
            self.port_OK = False

    def check_capture(self):
        """
        Check if Arduino board received capture command.
        """
        r = self.board.readline()
        st = r.decode("utf-8")
        if len(r) > 0:
            if st.strip() == "y":  # reply
                return True
            else:
                return False
        else:
            return False

    def open_port(self):
        """
        Open serial port to Arduino board.
        """
        try:
            self.board = serial.Serial(port=self.port, baudrate=115200, timeout=2.0)
        except:
            self.port_OK = False
        else:
            time.sleep(2)
            self.check_port()

    def get_ports(self):
        """
        Get serial ports.
        """
        ps = serial.tools.list_ports.comports()
        ports = []
        for p, desc, hwid in sorted(ps):
            ports.append(p)
        return ports
