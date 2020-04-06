import os
import sys
import time
import inspect
import numpy as np
from multiprocessing import Process

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PLATFORM = os.path.join(HERE, "..")
sys.path.append(PLATFORM)

import utils.mail as mail
import utils.json_utils as json
import operations.constants.common as cst
import operations.constants.filepaths as fp
#import operations.pH_module.pH_control as DrDAQ

from utils.logger import Logger
from operations.camera.camera_control import CameraControl
from operations.wheel.wheel_control import MultiBoardSystem


class Manager(object):
    """
    Class for managing all aspects of the platform
    Gives methods for controlling the camera, wheel, pumps etc

    Args:
        name (str): Name of the unit
        flag (int): Flag to specify which system to use
            0: Frodo
            1: Sam
    """
    def __init__(self, flag):
        # Initialise the pH server -- NYI
        # self.pH_server = Process(target=DrDAQ.run_server, args=())
        # self.pH_server.start()
        
        # Initialise the camera and wheel control
        self.camera = CameraControl()
        self.wheel = MultiBoardSystem(flag)

        # Initialise the logger
        self.logger = Logger(fp.create_log_file(self.wheel.name), self.wheel.name)
        self.log("Successfully instantiated Wheel: {}".format(self.wheel.name))

        # Obtain the pH calibrations from calibrations folder (pH 4, 7, 10) -- NYI
        # self.pH_calibrations = json.read(fp.get_ph_calibration_path(self.wheel.name))


    def calibrate_pumps(self):
        """
        Calibrates the pumps on the MultiBoardSystem
        """
        self.wheel.calibrate_system()

    
    def dispense(self, pump_name, volume):
        """
        Dispenses a volume from a pump

        Args:
            pump_name (str): Name of the pump
            volume (int/float): Volume to dispense
        """
        self.log("Dispensing volume {}ml from pump {}".format(volume, pump_name))
        self.wheel.dispense(pump_name, volume)


    def run_pump(self, pump_name, duration):
        """
        Runs a pump for a specific duration

        Args:
            pump_name (str): Name of the pump
            duration (int/float): Duration to run for
        """
        self.log("Running pump {} for {} seconds".format(pump_name, duration))
        self.wheel.run(pump_name, duration)

    
    def prime_pumps(self, *ignore):
        """
        Primes the pumps on the system by running for a set duration

        Args:
            ignore (str): Pumsp to ignore
        """
        self.log("Priming all pumps")
        for pump in cst.PUMPS:
            if pump in ignore:
                continue
            self.run_pump(pump, cst.PRIME_TIME)
        self.log("Pumps primed")

    
    def turn_wheel(self, n_turns):
        """
        Turns the Geneva wheel

        Args:
            n_turns (int): Number of turns to perform
        """
        self.wheel.turn_wheel(n_turns)

    
    def lower_module(self, mod_name):
        """
        Lowers a modular driver

        Args:
            mod_name (str): Name of the modular driver
        """
        self.wheel.lower_module(mod_name)

    
    def home_module(self, mod_name):
        """
        Homes a modular driver

        Args:
            mod_name (str): Name of the modular driver
        """
        self.wheel.home_module(mod_name)


    def start_wheel_stirring(self):
        """
        Starts the stirrers under the wheel
        """
        self.wheel.set_stir_rate(250)
        time.sleep(0.5)
        self.wheel.set_stir_rate(35)

    
    def stop_wheel_stirring(self):
        """
        Turns off the stirrers under the wheel
        """
        self.wheel.set_stir_rate(0)


    def start_stirrer_plate(self):
        """
        Starts the stirrer plate fans
        """
        self.wheel.set_stirrer_plate_rate(250)
        time.sleep(0.5)
        self.wheel.set_stirrer_plate_rate(30)

    
    def stop_stirrer_plate(self):
        """
        Stops the stirrer plate fans
        """
        self.wheel.set_stirrer_plate_rate(0)


    def take_pH_measurement(self):
        """
        Measures the pH of the solution
        If calibrations exist, performs a linear fit of the measured value

        Returns:
            value (float): Measured pH of the solution
        """
        self.log("Measuring pH of sample solution")
        value = self.wheel.take_pH_measurement()

        # pH has not been calibrated, logs raw value instead
        if 0 in self.pH_calibrations.values():
            self.log("Warning -- pH Calibrations have not been set, raw value is {}".format(value))
        else:
            # Converts pH value and raw measurement into list
            pH_value = [int(x) for x in self.pH_calibrations.keys()]
            raw_value_list = [x for x in self.pH_calibrations.values()]

            # Linear fit with a bit of math to obtain the actual pH value
            x = np.array(raw_value_list, dtype=np.float64)
            y = np.array(pH_value, dtype=np.float64)
            fit  = np.polyfit(x,y,1)
            value = float(value) * (fit[0]) + fit[1]
            self.log("pH Measured: {}".format(value))


    
    def record_video(self, save_loc, duration):
        """
        Records a video and saves to file

        Args:
            save_loc (str): Location to save the video
            duration (int/float): Duration to record for
        """
        self.log("Recording video ({}) for {}s".format(save_loc, duration))
        self.camera.record(save_loc, duration)

    
    def take_image(self, save_loc):
        """
        Take an image with the camera

        Args:
            save_loc (str): Location to save the image
        """
        self.camera.take_image(save_loc)

    
    def log(self, msg):
        """
        Logs a message using the Logger
        """
        self.logger.info(msg)

    
    def send_mail(self, msg, flag=0):
        """
        Sends an email to each address in the common constants list

        Args:
            msg (str): Message to send
            flag (int): Flag to determine the type of message
                0: Basic notification
                1: System has crashed
        """
        mail.notify(cst.PLATFORM_NAME, cst.EMAILS, msg, flag=flag)


    def cleanup(self):
        """
        Kills all threads
        """
        self.log("Killing connection to pH Server")
        # self.wheel.kill_pH_server()
        # self.pH_server.join()
