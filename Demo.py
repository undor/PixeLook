from PixeLook import PixeLook
import configparser


def create_political_cv_images():
    import cv2
    from UtilsAndModels.Defines import face_cascade, predictor
    import random
    import numpy as np
    import dlib
    from imutils import face_utils

    img = cv2.imread("gantz.jpg")
    rects_cv = face_cascade.detectMultiScale(img)
    for (x, y, w, h) in rects_cv:
        R = random.randint(0, 255)
        G = random.randint(0, 255)
        B = random.randint(0, 255)
        # cv2.rectangle(img, (x, y), (x + w, y + h), (int(R), int(G), int(B)), 2)
    if np.size(rects_cv) > 0:
        rects_cv_to_dlib = dlib.rectangle(rects_cv[0][0], rects_cv[0][1], rects_cv[0][0] + rects_cv[0][2],
                                          rects_cv[0][1] + rects_cv[0][3])
        prediction = predictor(img, rects_cv_to_dlib)
        prediction = face_utils.shape_to_np(prediction)
        # (x, y, w, h) = face_utils.rect_to_bb(rect)
        for (x, y) in prediction:

            cv2.circle(img, (x, y), 1, (0, 255, 0), -1)

    img_height = img.shape[0]
    img_width = img.shape[1]
    img = cv2.resize(src=img, dsize=(int(img_width*4.5),int(img_height*4.5) ))

    cv2.imshow("img", img)
    cv2.waitKey(0)
    exit(0)


def str_to_bool(str):
    return True if str == "true" else False


def PixeLook_from_config(settings):
    params = ['screen_size', 'camera_number', 'calib_ratio']
    for param in params:
        if param not in settings:
            print("missing", param, "in config file.")
            exit()
        settings[param] = float(settings[param])
    logs = False if "logs" not in settings else str_to_bool(settings['logs'])
    return PixeLook(screen_size=settings["screen_size"], camera_number=settings["camera_number"],
                    calib_ratio=settings["calib_ratio"], logs=logs)


def __main__():
    # create_political_cv_images()
    config = configparser.ConfigParser()
    config.read("config.txt")
    config = {s: dict(config.items(s)) for s in config.sections()}
    my_px_gt = PixeLook_from_config(config['settings'])

    mode = "none" if "mode" not in config["operation"] else config["operation"]["mode"]
    webcam = False if "webcam" not in config["operation"] else str_to_bool(config["operation"]["webcam"])
    post = False if "post" not in config["operation"] else str_to_bool(config["operation"]["post"])

    my_px_gt.calibrate()

    if mode == "dots":
        my_px_gt.draw_live()
    elif mode == "screenshots":
        my_px_gt.start_screen_shots(post=post,webcam=webcam)
    elif mode == "none":
        my_px_gt.run_in_background(post=post)


if __name__ == "__main__":
    __main__()
