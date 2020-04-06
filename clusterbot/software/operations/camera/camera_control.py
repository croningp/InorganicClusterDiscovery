import os
import sys
import inspect

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_path = os.path.join(HERE, "..", "..")
op_path = os.path.join(HERE, "..")

sys.path.append(root_path)
sys.path.append(op_path)

from base_layer.camera import camera_setup

class CameraControl(object):
    """
    Class for controlling a camera via OpenCV
    """
    def __init__(self):
        pass


    def record(self, video_name, duration):
        """
        Records a video to file

        Args:
            video_name (str): Path to save the video
            duration (int/float): Duration of the recording
        """
        print("Taking video...")
        camera_setup.record_video(video_name, duration)


    def take_image(self, save_loc):
        """
        Takes an image of the reaction

        Args:
            save_loc (str): Path to save the image
        """
        print("Taking image...")
        camera_setup.take_image(save_loc)
