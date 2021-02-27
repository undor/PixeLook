from PixeLook import PixeLook
import configparser


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
        my_px_gt.start_screen_shots(post=post, webcam=webcam)
    elif mode == "none":
        my_px_gt.run_in_background(post=post)


if __name__ == "__main__":
    __main__()
