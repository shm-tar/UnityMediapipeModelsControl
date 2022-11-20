from typing import Tuple
import os
import cv2
import dlib
from imutils import face_utils


class FaceMeshDLib:
    def __init__(self,
                 model="shape_predictor_68_face_landmarks.dat") -> None:
        path_to_model = os.path.dirname(os.path.abspath(__file__))
        self.model = f"{path_to_model}/{model}"
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.model)

    def place_mesh(self, image) -> Tuple:
        self.image_height, self.image_width, self.image_channels = image.shape

        self.points_coords = []
        image = cv2.flip(image, 1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 0)

        for (_, rect) in enumerate(rects):
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            self.shape_ext = shape

            for (x, y) in shape:
                cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                # print(f"Coords: {(x, y)}")
                self.points_coords.append([x, y])

        return image, self.points_coords

    def test_landmarks(self) -> None:
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            _, image = cap.read()
            image = cv2.flip(image, 1)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rects = self.detector(gray, 0)

            for (_, rect) in enumerate(rects):
                shape = self.predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                for (x, y) in shape:
                    cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                    # print(f"Coords: {(x, y)}")

            cv2.imshow("Output", image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        cap.release()
