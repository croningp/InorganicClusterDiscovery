"""
.. module:: wheel_control
    :platform: Unix
    :synopsis: Module for interfacing with the Commanduino core device in the Base Layer

.. moduleauthor:: Graham Keenan <https://github.com/ShinRa26>

"""

import os
import sys
import time
import inspect

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_path = os.path.join(HERE, "..", "..")
op_path = os.path.join(HERE, "..")
sys.path.append(op_path)
sys.path.append(root_path)

import constants.common as cst
import utils.json_utils as json
import constants.filepaths as fp
from base_layer.pH_module import DrDAQ_Client
from base_layer.commanduino_setup.core_device import CoreDevice
from base_layer.commanduino_setup.core_device import CommanduinoInitError


class WheelControl(CoreDevice):
    """
    Class for controlling a Geneva Wheel system
    Contains methods for rotation, modular drivers, pumps, etc.
    Assumes the user has at least one Geneva wheel, one modular driver, and one peristaltic
    pump attached to their rig.

    Inherits:
        CoreDevice: Commanduino Base Device

    Args:
        config (str): Path to the config

    Raises:
        CommanduinoInitError (Exception): Empty device dictionary
    """
    def __init__(self, config):
        super().__init__(config)
        if not self.mgr.devices:
            raise CommanduinoInitError("Empty device dictionary")


    def turn_wheel(self, n_turns, wait=True):
        """
        Turns the geneva wheel n_turns times

        Args:
            n_turns (int): Number of turns
        """
        if self.valid_device(cst.WHEEL):
            drive_wheel = self.get_device_attribute(cst.WHEEL)
            for _ in range(n_turns):
                drive_wheel.move(cst.FULL_WHEEL_TURN, wait=wait)
        else:
            print("Device \"{}\" cannot be found on this system.".format(cst.WHEEL))


    def move_module(self, mod_name, pos, wait=True):
        """
        Moves the modular driver to a set position

        Args:
            mod_name (str): Name of the module
            pos (int/float): Number of steps to move
            wait (bool): Wait for the device to be idle, default set to True
        """
        if pos < 0 or pos > cst.MODULE_LOWER:
            print("Position is out of range: {}".format(pos))
            return

        if self.valid_device(mod_name):
            module = self.get_device_attribute(mod_name)
            module.move_to(-pos, wait=wait) # -ve due to inverted direction
        else:
            print("Device \"{}\" cannot be found on this system.".format(mod_name))

    
    def lower_module(self, mod_name, wait=True):
        """
        Lower a modular driver

        Args:
            mod_name (str): Name of the modular driver
            wait (bool): Wait for the device to be idle
        """
        self.move_module(mod_name, cst.MODULE_LOWER, wait=wait)


    def home_module(self, mod_name, wait=True):
        """
        Brings the module back to its home position

        Args:
            mod_name (str): Name of the module
            wait (bool): Wait for the device to be idle, default set to true
        """
        if self.valid_device(mod_name):
            module = self.get_device_attribute(mod_name)
            module.home(wait=wait)
        else:
            print("Device \"{}\" cannot be found on this system.".format(mod_name))

    
    def pump_by_time(self, pump_name, num_secs):
        """
        Runs a peristaltic pump for num_secs time

        Args:
            pump_name (str): Name of the pump
            num_secs (int/float): Number of seconds to run for
        """
        if self.valid_device(pump_name):
            pump = self.get_device_attribute(pump_name)
            curr_time = time.time()
            while time.time() < (curr_time + num_secs):
                pump.move(cst.PUMP_INCREMENT)

    
    def pump_by_volume(self, pump_name, volume, calibration):
        """
        Runs a peristaltic pump for x seconds, determined by the passed volume
        Needs calibration first

        Args:
            pump_name (str): Name of the pump
            volume (int/float): Volume to dispense
        """
        if self.valid_device(pump_name):
            # Get pump and runtime
            pump = self.get_device_attribute(pump_name)
            seconds_of_runtime = (volume/(calibration/cst.MINUTE))

            # Set current position to 0
            pump.set_current_position(0)
            current_time = time.time()

            # Dispense for the given runtime
            while time.time() < (current_time + seconds_of_runtime):
                pump.move_to(cst.PUMP_INCREMENT)
                pump.set_current_position(0)
        else:
            print("Pump \"{}\" is not recognized.".format(pump_name))


    # def calibrate_pump(self, pump_name):
    #     """
    #     Calibrates the pump by running it for a minute, comparing weight
    #     before and after

    #     Args:
    #         pump_name (str): Name of the pump

    #     Returns:
    #         calib (float): Dispense rate in ml s-1
    #     """
    #     print("Calibrating pump: {}".format(pump_name))
    #     print("Weight before: ")
    #     before = input()
    #     print("Running {} for 60 seconds.".format(pump_name))
    #     self.pump_by_time(pump_name, cst.MINUTE)
    #     print("Weight after: ")
    #     after = input()

    #     calibration = "%.4f"%(float(after) - float(before))
    #     return float(calibration)


    def set_stir_rate(self, value):
        """
        Sets the power limit of the fans

        Args:
            value (int): 0-255
        """
        if self.valid_device(cst.FANS):
            fans = self.get_device_attribute(cst.FANS)
            fans.set_pwm_value(value)
        else:
            print("Name \"{}\" is not recognised for fans".format(cst.FANS))


    def set_stirrer_plate_rate(self, value):
        """
        Activates the stirrer plate

        Args:
            value (int): 0-255
        """
        if self.valid_device(cst.STIRRER):
            plate = self.get_device_attribute(cst.STIRRER)
            plate.set_pwm_value(value)
        else:
            print("Name \"{}\" is not recognised for fans".format(cst.STIRRER))



class MultiBoardSystem(object):
    """
    Class for supporting two Commanduino boards in the Wheel System
    Main is the board that controls the wheel movement, modular driver, and pumps
    Secondary is purely for pumps

    Args:
        name (str): Name of the system
        flag (int): Flag for selecting Frodo/Sam etc.
    """
    def __init__(self, flag):
        if flag == 0:
            self.name = cst.FRODO
            self.main = WheelControl(fp.FRODO_CFG[0])
            self.secondary = WheelControl(fp.FRODO_CFG[1])
        elif flag == 1:
            self.name = cst.SAM
            self.main = WheelControl(fp.SAM_CFG[0])
            self.secondary = WheelControl(fp.SAM_CFG[1])

        self.calibrations = self.get_calibrations()
        if not self.calibrations_ok():
            print("!!! CALIBRATION NEEDED !!!")


    def calibrations_ok(self):
        """
        Checks if the calibrations have been set

        Returns:
            ok (bool): The calibrations exist
        """
        if self.calibrations:
            return True
        return False


    def get_calibrations(self):
        """MINUTE
        Attempts to read the calibrations file

        Returns:
            calibrations (Dict): The calibrations for each of the pumps
            empty (Dict): An empty dictionary if the calibrations don't exist
        """
        try:
            filename = self.name + ".json"
            calib_path = os.path.join(fp.CALIBRATIONS, filename)
            print(calib_path)
            calibrations = json.read(calib_path)
            print("Calibrations found: {}".format(calibrations))
            return calibrations
        except:
            print("Cannot find calibration file: {}\nReturning empty calibrations.".format(os.path.relpath(calib_path)))
            return {}

    
    def write_calibrations(self, calibrations):
        """
        Writes the calibrations to file

        Args:
            calibrations (Dict): Pump calibrations in ml per minute
        """
        filename = self.name + ".json"
        calib_path = os.path.join(fp.CALIBRATIONS, filename)
        json.write(calibrations, calib_path)


    def calculate_calibration(self, before, after):
        """
        Calculates the flow rate in ml per minute of a given pump

        Args:
            before (str): Weight of vial before water addition
            after (str): Weight of vial after water addition

        Returns:
            calibration (float): Flow rate in ml per minute
        """
        calibration = "%.4f"%(float(after) - float(before))
        return float(calibration)


    def calibrate_system(self):
        """
        Calibrates all the pumps on the system
        Iterates through a list of pumps, determines what board they belong to and calibrates each pump
        Writes calibrations out to file once done
        """
        for pump in cst.PUMPS:
            calibration = 0
            
            # Calibrate each pump PUMP_CALIBRATION_COUNTER times
            print("Calibrating pump: {}".format(pump))
            for _ in range(cst.PUMP_CALIBRATION_COUNTER):
                before = input("Weight before: ")
                if pump in self.main.devices:
                    self.main.pump_by_time(pump, cst.MINUTE)
                    self.main.turn_wheel(cst.SINGLE_TURN)
                elif pump in self.secondary.devices:
                    self.secondary.pump_by_time(pump, cst.MINUTE)
                    self.main.turn_wheel(cst.SINGLE_TURN)
                else:
                    print("Unrecognised pump: {}".format(pump))
                after = input("Weight after: ")
                calibration += self.calculate_calibration(before, after)
            
            # Set the calibration 
            self.calibrations[pump] = calibration/cst.PUMP_CALIBRATION_COUNTER
            print("Calibration for pump \"{}\": {}ml per minute".format(pump, self.calibrations[pump]))
        
        self.write_calibrations(self.calibrations)
    

    def dispense(self, pump_name, volume):
        """
        Dispenses a volume from a pump

        Args:
            pump_name (str): Name of the pump
            volume (int/float): Volume to dispense
        """
        if pump_name in self.main.devices:
            self.main.pump_by_volume(pump_name, volume, self.calibrations[pump_name])
        elif pump_name in self.secondary.devices:
            self.secondary.pump_by_volume(pump_name, volume, self.calibrations[pump_name])
        else:
            print("No pump called \"{}\" on any system".format(pump_name))


    def run(self, pump_name, duration):
        """
        Runs a specific pump for a set duration

        Args:
            pump_name (str): Name of the pump_name
            duration (int/float): Duration to run for
        """
        if pump_name in self.main.devices:
            self.main.pump_by_time(pump_name, duration)
        elif pump_name in self.secondary.devices:
            self.secondary.pump_by_time(pump_name, duration)
        else:
            print("No pump called \"{}\" on any system".format(pump_name))


    def take_pH_measurement(self):
        """
        Lowers the pH modular driver and measures the pH of the solution using the DrDAQ client

        Returns:
            value (float): Raw mV value of the pH reading
        """
        self.lower_module(cst.PH)
        value = DrDAQ_Client.receive_pH()
        self.home_module(cst.PH)

        return value


    def kill_pH_server(self):
        """
        Kills the connection to the pH server
        """
        DrDAQ_Client.kill_server()

    
    def turn_wheel(self, n_turns):
        """
        Turns the wheel on the main board

        Args:
            n_turns (int): Number of turns to perform
        """
        self.main.turn_wheel(n_turns)


    def lower_module(self, mod_name):
        """
        Lowers a modular driver to it's lowest point

        Args:
            mod_name (str): Name of the modular driver
        """
        self.main.lower_module(mod_name)


    def home_module(self, mod_name):
        """
        Sends a modular driver to its home position

        Args:
            mod_name (str): Name of the modular driver
        """
        self.main.home_module(mod_name)
    

    def set_stir_rate(self, value):
        """
        Sets the stirring rate of the fans

        Args:
            value (int): 0-255
        """
        self.main.set_stir_rate(value)
    

    def set_stirrer_plate_rate(self, value):
        """
        Sets the stirring rate for the stirrer plate

        Args:
            value (int): 0-255
        """
        self.main.set_stirrer_plate_rate(value)