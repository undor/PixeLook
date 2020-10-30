import cv2
import numpy as np
import pyautogui
from UtilsAndModels.Defines import capture_input_width,capture_input_height
from Tests.TestIDE import Test_Manager


def screen_record(test_manager: Test_Manager, size_mm: int = 50, frames: int = 100,alpha=0.5):
    pixel_per_mm = test_manager.gaze_manager.pixel_per_mm
    tkinter_to_real_ration = 2
    size = int(size_mm * pixel_per_mm * tkinter_to_real_ration *2)
    # display screen resolution, get it from your OS setting
    out_screen = cv2.VideoWriter("output_screen.avi", 0, 2, (test_manager.width*2,test_manager.height*2))
    out_webcam = cv2.VideoWriter("output_webcam.avi", 0, 2, (capture_input_width, capture_input_height))

    for i in range(frames):
        print("in frame ", i, " of ", frames)
        # get Pixel
        cur_pix = np.array(test_manager.get_pixel_combined())
        print("cur pixel is", cur_pix)
        # Fix ratio from tkinter to real screen
        cur_pix = cur_pix*tkinter_to_real_ration

        # get shots
        screen_shot = pyautogui.screenshot()
        webcam_shot = test_manager.gaze_manager.env.webcam_shot

        # edit the screenshot
        frame = np.array(screen_shot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        overlay = frame.copy()
        overlay = cv2.circle(overlay, (int(cur_pix[0]), int(cur_pix[1])), 300, (255, 0, 0), -1)
        final_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        # write the frames
        out_screen.write(final_frame)
        out_webcam.write(webcam_shot)
    # make sure everything is closed when exited
    out_screen.release()
    out_webcam.release()


