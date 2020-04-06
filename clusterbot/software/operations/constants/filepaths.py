"""
List of filepaths used within the project
"""

import os
import sys
import time
import inspect

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# Common places
OP = os.path.join(HERE, "..")
PLATFORM = os.path.join(OP, "..")
ROOT = os.path.join(PLATFORM, "..", "..")
RUN = os.path.join(ROOT, "clusterbot_run")
LOG = os.path.join(RUN, "logs")
DATA = os.path.join(RUN, "data")
CONFIGS = os.path.join(OP, "configs")
CALIBRATIONS = os.path.join(OP, "constants", "calibrations")

# Config files for the wheel
FRODO1_CFG = os.path.join(CONFIGS, "frodo1.json")
FRODO2_CFG = os.path.join(CONFIGS, "frodo2.json")
SAM1_CFG = os.path.join(CONFIGS, "sam1.json")
SAM2_CFG = os.path.join(CONFIGS, "sam2.json")
FRODO_CFG = [FRODO1_CFG, FRODO2_CFG]
SAM_CFG = [SAM1_CFG, SAM2_CFG]

# Calibrations
def get_ph_calibration_path(name):
    """
    Gets the pH calibrations for the specified system

    Args:
        name (str): Name of the system (Frodo, Sam etc.)
    """
    return os.path.join(CALIBRATIONS, "{}_pH_calibrations.json".format(name))


# Log file
def create_log_file(name):
    """
    Creates a name for the log file with time and date

    Args:
        name (str): Name of the platform
    """
    return os.path.join(LOG, "{}_{}.log".format(name, time.strftime("%Y%m%d_%H%M")))
