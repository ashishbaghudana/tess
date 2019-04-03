import threading
import time


class BackgroundFunction(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, func, interval=1, *args, **kwargs):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        :param func: Function to execute
        """
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs

        thread = threading.Thread(target=self.run, args=())
        # Daemonize thread
        thread.daemon = True
        # Start the execution
        thread.start()

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)
