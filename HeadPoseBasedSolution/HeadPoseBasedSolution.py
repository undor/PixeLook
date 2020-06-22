from Defines import *
import cv2


def start_camera_sol1 ():
        model = GazeModel.load_model()
        cap = set_camera(1280, 720)
        fps = fpsHelper()
        while True:
            ret, img = cap.read()
            cur_frame = FrameData(img)
            if cur_frame.face_landmark_detect():

                cur_frame.head_pose_detect()
                cur_frame.eyes_detect()
                cur_frame.pre_proccess_for_net()    #TODO - Improvments for pre proccess for net

                gaze_angles = GazeModel.use_net(model, cur_frame)
                gaze_vector = angle_to_vector(gaze_angles)

                #TODO - ADD after proccess  method to get position on screen

                fps.reg_time()
                add_data_on_img(cur_frame, gaze_angles, fps.get_fps())
                cv2.imshow("Output", cur_frame.debug_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

