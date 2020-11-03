from PixeLook import PixeLook

def __main__():
    my_px_gt = PixeLook(screen_size=24, camera_number=0)
    my_px_gt.calibrate()

    my_px_gt.set_screen_shots(with_webcam=True)
    my_px_gt.start_screen_shots(200)


if __name__ == "__main__":
    __main__()
