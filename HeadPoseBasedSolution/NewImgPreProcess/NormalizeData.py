from UtilsAndModels.Defines import *


def normalizeData(img, face, hr, ht, cam):
    # normalized camera parameters
    focal_norm = 960  # focal length of normalized camera
    distance_norm = 550  # normalized distance between eye and camera
    roiSize = (60, 36)  # size of cropped eye image

    img_u = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # compute estimated 3D positions of the landmarks

    ht = ht.reshape((3, 1))
    hR = cv2.Rodrigues(hr)[0]  # rotation matrix
    Fc = np.dot(hR, face) + ht  # 3D positions of facial landmarks
    re = 0.5 * (Fc[:, 0] + Fc[:, 1]).reshape((3, 1))  # center of left eye
    le = 0.5 * (Fc[:, 2] + Fc[:, 3]).reshape((3, 1))  # center of right eye

    # normalize each eye
    data = []
    for et in [re, le]:
        # ---------- normalize image ----------
        distance = np.linalg.norm(et)  # actual distance between eye and original camera

        z_scale = distance_norm / distance
        cam_norm = np.array([
            [focal_norm, 0, roiSize[0] / 2],
            [0, focal_norm, roiSize[1] / 2],
            [0, 0, 1.0],
        ])
        S = np.array([  # scaling matrix
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, z_scale],
        ])

        hRx = hR[:, 0]
        forward = (et / distance).reshape(3)
        down = np.cross(forward, hRx)
        down /= np.linalg.norm(down)
        right = np.cross(down, forward)
        right /= np.linalg.norm(right)
        R = np.c_[right, down, forward].T  # rotation matrix R
        W = np.dot(np.dot(cam_norm, S), np.dot(R, np.linalg.inv(cam)))  # transformation matrix

        img_warped = cv2.warpPerspective(img_u, W, roiSize)  # image normalization
        img_warped = cv2.equalizeHist(img_warped)

        # ---------- normalize rotation ----------
        hR_norm = np.dot(R, hR)  # rotation matrix in normalized space
        hr_norm = cv2.Rodrigues(hR_norm)[0]  # convert rotation matrix to rotation vectors

        # --------- Convert to euler angle -------

        # hr_theta = np.arcsin(-1 * hr_norm[1])
        # hr_phi = np.arctan2(-1 * hr_norm[0], -1 * hr_norm[2])
        # hr_res = np.array([hr_theta, hr_phi]).T
        # print("before hr res is: ", hr_res)
        M_HP = cv2.Rodrigues(hr_norm)[0]
        a = M_HP[2][0]
        b = M_HP[2][1]
        c = M_HP[2][2]
        headpose_theta = np.arcsin(b)
        headpose_phi = np.arctan2(a, c)
        hr_res =np.array([[headpose_theta, headpose_phi]])
        data.append([img_warped, hr_res])

    return data
