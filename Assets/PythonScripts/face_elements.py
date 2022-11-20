import numpy as np

eye_idx = [
    [33, 7, 163, 144, 145, 153, 154, 155, 133, 246, 161, 160, 159, 158, 157, 173],
    [263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]]


def np_sum(image_points, f_index: int, s_index: int, is_left=False):
    if is_left:
        return np.true_divide(
            np.sum([image_points[eye_idx[0][f_index]],
                   image_points[eye_idx[0][s_index]]], axis=0),
            2)
    elif not is_left:
        return np.true_divide(
            np.sum([image_points[eye_idx[1][f_index]],
                   image_points[eye_idx[1][s_index]]], axis=0),
            2)


def eye_aspect_ratio(image_points, side):
    fst_point = scnd_point = trd_point = frth_point = ffth_point = sx_point = eyebrow = 0

    if side == 1:
        scnd_point = np_sum(image_points, 10, 11, True)
        trd_point = np_sum(image_points, 13, 14, True)
        sx_point = np_sum(image_points, 2, 3, True)
        ffth_point = np_sum(image_points, 5, 6, True)

        fst_point = image_points[eye_idx[0][0]]
        frth_point = image_points[eye_idx[0][8]]

        eyebrow = image_points[105]

    elif side == 2:
        trd_point = np_sum(image_points, 10, 11, False)
        scnd_point = np_sum(image_points, 13, 14, False)
        ffth_point = np_sum(image_points, 2, 3, False)
        sx_point = np_sum(image_points, 5, 6, False)

        fst_point = image_points[eye_idx[1][8]]
        frth_point = image_points[eye_idx[1][0]]

        eyebrow = image_points[334]

    ear = np.linalg.norm(scnd_point-sx_point) + np.linalg.norm(trd_point-ffth_point)
    ear /= (2 * np.linalg.norm(fst_point-frth_point) + 1e-6)
    ear = ear * (np.linalg.norm(eyebrow -
                 image_points[2]) / np.linalg.norm(image_points[6]-image_points[2]))
    return ear


def mouth_aspect_ratio(image_points):
    fst_point = image_points[78]
    scnd_point = image_points[81]
    trd_point = image_points[13]
    frth_point = image_points[311]
    ffth_point = image_points[308]
    sx_point = image_points[402]
    svn_point = image_points[14]
    egh_point = image_points[178]

    mar = np.linalg.norm(scnd_point-egh_point) + np.linalg.norm(trd_point-svn_point) + np.linalg.norm(frth_point-sx_point)
    mar /= (2 * np.linalg.norm(fst_point-ffth_point) + 1e-6)
    return mar


def mouth_distance(image_points):
    fst_point = image_points[78]
    ffth_point = image_points[308]
    return np.linalg.norm(fst_point-ffth_point)


def detect_iris(image_points, iris_image_points, side):
    iris_img_point = -1
    fst_point = frth_point = 0
    eye_y_high = eye_y_low = 0
    x_rate = y_rate = 0.5

    if side == 1:
        iris_img_point = 468

        eye_key_left = eye_idx[0]
        fst_point = image_points[eye_key_left[0]]
        frth_point = image_points[eye_key_left[8]]

        eye_y_high = image_points[eye_key_left[12]]
        eye_y_low = image_points[eye_key_left[4]]

    elif side == 2:
        iris_img_point = 473

        eye_key_right = eye_idx[1]
        fst_point = image_points[eye_key_right[8]]
        frth_point = image_points[eye_key_right[0]]

        eye_y_high = image_points[eye_key_right[12]]
        eye_y_low = image_points[eye_key_right[4]]

    p_iris = iris_image_points[iris_img_point - 468]

    vec_p1_iris = [p_iris[0] - fst_point[0], p_iris[1] - fst_point[1]]
    vec_p1_p4 = [frth_point[0] - fst_point[0], frth_point[1] - fst_point[1]]

    x_rate = (np.dot(vec_p1_iris, vec_p1_p4) /
              (np.linalg.norm(fst_point-frth_point) + 1e-06)) / (np.linalg.norm(fst_point-frth_point) + 1e-06)

    vec_eye_h_iris = [p_iris[0] - eye_y_high[0], p_iris[1] - eye_y_high[1]]
    vec_eye_h_eye_l = [eye_y_low[0] -
                       eye_y_high[0], eye_y_low[1] - eye_y_high[1]]

    y_rate = (np.dot(vec_eye_h_eye_l, vec_eye_h_iris) / (np.linalg.norm(eye_y_high -
              eye_y_low) + 1e-06)) / (np.linalg.norm(eye_y_high - eye_y_low) + 1e-06)

    return x_rate, y_rate
