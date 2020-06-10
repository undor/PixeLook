from Defines import *

def print_gaze_line(img,eye_center,gaze_vector,r_vec,t_vec):
    length = 0.0001
    gaze_vector = gaze_vector / np.linalg.norm(gaze_vector)
    points =np.array ([eye_center  + length*gaze_vector])
    (eye_end_point2D, jacobian) = cv2.projectPoints(points, r_vec, t_vec, camera_matrix_a, dist_coeff_a)
    p1 = (int(eye_center[0]), int(eye_center[1]))
    p2 = (int(eye_end_point2D[0][0][0]), int(eye_end_point2D[0][0][1]))
    cv2.line(img, p1, p2, (255, 255, 0), 2)
    return img

def show_debug_img(frame, gaze_angles, fps):
    gaze_angles=gaze_angles[0]
    head_angles = frame.get_head_pose()
    cv2.putText(frame.debug_img , "gaze angles: " + str(gaze_angles[0])  +  "  " + str(gaze_angles[1]), (100,100) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(frame.debug_img , "head angles: " + str(head_angles[0])  +  "  " + str(head_angles[1]), (100,200) , font, 1, (0, 150, 0), 2, cv2.LINE_4)
    cv2.putText(frame.debug_img , "fps  :  " + str(fps), (100, 300), font, 1,(0, 150, 0), 2, cv2.LINE_4)
    cv2.imshow("Output", frame.debug_img)

def set_camera(width,height):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap

def start_camera ():
        model = GazeModel.load_model()
        cap = set_camera(1280,720)
        fps = fpsHelper()
        while True:
            cur_frame = FrameData(cap.read(1))
            if cur_frame.face_landmark_detect():
                cur_frame.head_pose_detect()
                cur_frame.eyes_detect()
                cur_frame.pre_proccess_for_net()

                gaze_angles = GazeModel.use_net(model, cur_frame)
                gaze_vector = angle_to_vector(gaze_angles)

                fps.reg_time()
                show_debug_img(cur_frame, gaze_angles, fps.get_fps())


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
