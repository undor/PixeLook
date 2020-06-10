from Defines import *
import cv2

def add_data_on_img(frame, gaze_angles, fps):
    gaze_angles=gaze_angles[0]
    head_angles = frame.get_head_pose()
    cv2.putText(frame.debug_img , "gaze angles: " + str(gaze_angles[0])  +  "  " + str(gaze_angles[1]), (100,100) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(frame.debug_img , "head angles: " + str(head_angles[0])  +  "  " + str(head_angles[1]), (100,200) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(frame.debug_img , "fps  :  " + str(fps), (100, 300), font, 1,(0, 150, 0), 2, cv2.LINE_4)


def set_camera(width,height):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap

def start_camera ():
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
