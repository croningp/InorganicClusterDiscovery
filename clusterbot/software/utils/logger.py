import os
import sys
import time
import socket
import inspect
import logging
import threading
from queue import Queue

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PLATFORM_NAME = "CLUSTERBOT"

TERMINATE = "TERMINATE"
ARKENSTONE = ("130.209.221.130", 9000) # Change to remote address (Ask Graham)

class Logger(object):
    """
    Logger class with option for remote connection to log server (Arkenstone)

    Args:
        logfile (str): The name of the logfile
        system_name (str): Name of the system, e.g. frodo, sam
        remote (bool): Use remote connection or not

    Note:
        System name is the name of the individual system within the platform
        As this is a multi wheel system that can run independently, each wheel has its own Logger
        The system name is the name of the wheel (Frodo, Sam). Without this, each wheel shares the same logger
        Sharing the logger is bad because there is no way of knowing which pump is associated with each wheel in the file
    """
    def __init__(self, logfile, system_name, remote=False):
        self.logger = self.get_logger(logfile, system_name)
        self.msg_queue = Queue()
        self.client = None

        if remote:
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect(ARKENSTONE)
                self.remote_initialisation()
                self.log_thread = threading.Thread(target=self.remote_log, args=())
                self.log_thread.start()
            except Exception as e:
                print("Error connecting to Arkenstone, continuing offline.\nError: {}".format(e))


    def __del__(self):
        """
        Destructor for cleaning up the remote connection thread
        """
        try:
            self.msg_queue.put("TERMINATE")
            self.log_thread.join()
        except:
            pass # Only cleans up the thread if remote is active


    def get_logger(self, logfile, name):
        """
        Sets up the logger object for logging messages

        Args:
            logfile (str): Path on where to save the log to
            name (str): Name of the system

        Returns:
            logger (Logger): Logger object
        """
        logger = logging.getLogger("{}_{}".format(PLATFORM_NAME, name.upper()))
        logger.setLevel(logging.INFO)

        fh = logging.FileHandler(filename=logfile)
        fh.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(name)s::%(levelname)s -- %(message)s")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger


    def info(self, msg):
        """
        Logs a message with the logger.
        If there is a remote connection, add it to the message queue to be sent

        Args:
            msg (str): Message to log
        """
        msg = "{} -- {}".format(time.strftime("%d_%m_%Y:%H%M"), msg)
        if self.client:
            self.msg_queue.put(msg)
        
        self.logger.info(msg)


    def remote_initialisation(self):
        """
        Initialises the platform on hte remote server
        """
        self.client.sendall("{}::INIT".format(PLATFORM_NAME).encode())

    def remote_log(self):
        """
        Thread method for sending logged messages to the remote server
        """
        while(True):
            msg = self.msg_queue.get()

            if msg == TERMINATE:
                self.cleanup()
                break

            msg = "{0}::LOG::{1}".format(PLATFORM_NAME, msg)
            self.client.sendall(msg.encode())


    def cleanup(self):
        """
        Closes down the connection to the remote server, if present
        """
        if self.client:
            print("Shutting down Arkenstone client...")
            self.client.shutdown(2)
            self.client.close()
