from PixeLook import PixeLook

def __main__():
    my_px_gt = PixeLook(screen_size=14, camera_number=0, calib_ratio=1)
    my_px_gt.calibrate()

    # Live Draw for demonstration
    my_px_gt.draw_live()
    # Screen recorder
    # my_px_gt.set_screen_shots(with_webcam=True)
    # my_px_gt.start_screen_shots(200)


if __name__ == "__main__":
    __main__()
