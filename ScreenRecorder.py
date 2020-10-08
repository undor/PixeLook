import cv2
import numpy as np
import pyautogui

from Tests.TestIDE import Test_Manager


def screen_record(test_manager: Test_Manager, size_mm: int = 50, frames: int = 70):
    pixel_per_mm = test_manager.gaze_manager.pixel_per_mm
    tkinter_to_real_ration = 2
    size = int(size_mm * pixel_per_mm * tkinter_to_real_ration *2)
    # display screen resolution, get it from your OS setting
    screen_size = (size, size)
    out = cv2.VideoWriter("output.avi", 0, 2, screen_size)
    print(" tkinter sizes: width",test_manager.width,"height",test_manager.height)

    for i in range(frames):
        # make a screenshot
        cur_pix = np.array(test_manager.get_pixel_with_method())
        cur_pix = cur_pix*tkinter_to_real_ration
        # fix ratio from tkinter to real screen
        img = pyautogui.screenshot(region=(cur_pix[0] - size/2 , cur_pix[1]- size/2, size, size))
        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)
        # convert colors from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # write the frame
        out.write(frame)
    # make sure everything is closed when exited
    out.release()
