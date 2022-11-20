from typing import Tuple
import cv2
import mediapipe as mp


class FaceMesh:
    """
    Detects the face and builds a mesh using face landmarks.
    """

    def __init__(self,
                 static_image_mode=False,
                 max_num_faces=1,
                 refine_landmarks=True,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5) -> None:
        self.static_image_mode = static_image_mode
        self.max_num_faces = max_num_faces
        self.refine_landmarks = refine_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.drawing_spec = self.mp_drawing.DrawingSpec(
            thickness=1,
            circle_radius=1)

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            self.static_image_mode,
            self.max_num_faces,
            self.refine_landmarks,
            self.min_detection_confidence,
            self.min_tracking_confidence)

    def place_mesh(self, image) -> Tuple:
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        self.res_output = self.face_mesh.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        self.image_height, self.image_width, self.image_channels = image.shape

        self.points_coords = []

        if self.res_output.multi_face_landmarks:
            for face_landmarks in self.res_output.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=self.drawing_spec)

                single_point_coord = []
                for i, landmark in enumerate(face_landmarks.landmark):
                    x, y = int(
                        landmark.x * self.image_width), int(landmark.y * self.image_height)
                    single_point_coord.append([x, y])

                self.points_coords.append(single_point_coord)
        return image, self.points_coords

    def test_landmarks(self) -> None:
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            success, img = cap.read()

            if not success:
                continue

            img, _ = self.place_mesh(img)
            cv2.imshow('MediaPipe FaceMesh', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
