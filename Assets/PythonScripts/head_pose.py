from typing import Tuple
import os
import cv2
import numpy as np


class HeadPose:
    def __init__(self,
                 img_size=(480, 640),
                 features_filename='mediapipe_features.txt') -> None:
        self.size = img_size

        path_to_features = os.path.dirname(os.path.abspath(__file__))
        self.features_filename = f"{path_to_features}/{features_filename}"

        self.model_points_full = self.read_features()

        self.focal_length = self.size[1]
        self.camera_center = (self.size[1] / 2, self.size[0] / 2)
        self.camera_matrix = np.array(
            [[self.focal_length, 0, self.camera_center[0]],
             [0, self.focal_length, self.camera_center[1]],
             [0, 0, 1]], dtype="double")

        self.dist_coeefs = np.zeros((4, 1))

        self.r_vec = None
        self.t_vec = None

    def read_features(self) -> np.ndarray:
        raw_value = []

        with open(self.features_filename, "r", encoding="utf-8") as filename:
            for line in filename:
                raw_value.append(line)

        model_points = np.array(raw_value, dtype=np.float32)
        model_points = np.reshape(model_points, (-1, 3))

        return model_points

    def solve_pose(self, img_points) -> Tuple:
        if self.r_vec is None:
            (_, rotation_vector, translation_vector) = cv2.solvePnP(
                self.model_points_full, img_points, self.camera_matrix, self.dist_coeefs)
            self.r_vec = rotation_vector
            self.t_vec = translation_vector

        (_, rotation_vector, translation_vector) = cv2.solvePnP(
            self.model_points_full,
            img_points,
            self.camera_matrix,
            self.dist_coeefs,
            rvec=self.r_vec,
            tvec=self.t_vec,
            useExtrinsicGuess=True)

        return (rotation_vector, translation_vector)

    def solve_pose_dlib(self, shape) -> Tuple:
        object_pts = np.float32([[6.825897, 6.760612, 4.402142],
                                 [1.330353, 7.122144, 6.903745],
                                 [-1.330353, 7.122144, 6.903745],
                                 [-6.825897, 6.760612, 4.402142],
                                 [5.311432, 5.485328, 3.987654],
                                 [1.789930, 5.393625, 4.413414],
                                 [-1.789930, 5.393625, 4.413414],
                                 [-5.311432, 5.485328, 3.987654],
                                 [2.005628, 1.409845, 6.165652],
                                 [-2.005628, 1.409845, 6.165652],
                                 [2.774015, -2.080775, 5.048531],
                                 [-2.774015, -2.080775, 5.048531],
                                 [0.000000, -3.116408, 6.097667],
                                 [0.000000, -7.415691, 4.070434]])

        image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                                shape[39], shape[42], shape[45], shape[31], shape[35],
                                shape[48], shape[54], shape[57], shape[8]])

        if self.r_vec is None:
            (_, rotation_vector, translation_vector) = cv2.solvePnP(
                object_pts, image_pts, self.camera_matrix, self.dist_coeefs)
            self.r_vec = rotation_vector
            self.t_vec = translation_vector

        (_, rotation_vector, translation_vector) = cv2.solvePnP(
            object_pts,
            image_pts,
            self.camera_matrix,
            self.dist_coeefs,
            rvec=self.r_vec,
            tvec=self.t_vec,
            useExtrinsicGuess=True)

        return (rotation_vector, translation_vector)
