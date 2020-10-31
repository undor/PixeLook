from PixelGetter import PixelGetter


def __main__():
    my_px_gt = PixelGetter(screen_size=13.3, camera_number=0)
    my_px_gt.calibrate()
    cur_pixel = my_px_gt.get_pixel()
    print (cur_pixel)

    my_px_gt.set_screen_shots(with_webcam=True)
    my_px_gt.start_screen_shots(50)


if __name__ == "__main__":
    __main__()
