import socket
import sys
import time

import cv2
import numpy as np

from face_elements import (detect_iris, eye_aspect_ratio, mouth_aspect_ratio,
                           mouth_distance)
from face_mesh_dlib import FaceMeshDLib
from face_mesh_mediapipe import FaceMesh
from head_pose import HeadPose
from head_pose_stabilizer import HeadPoseStabilizer
from utils import build_graph

PORT = 8000


def socket_connect() -> socket:
    """
    Connects to the specified port to communicate with Unity.
    """
    global PORT
    address = ('127.0.0.1', PORT)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        print(
            f"Address: {socket.gethostbyname(socket.gethostname())}:{str(PORT)}")
        return sock
    except OSError as error:
        print(f"{error}")
        sys.exit()


def socket_send(sock, args, debug=False) -> None:
    """
    Sends specified amount of bytes through the socket.
    """
    if not sock and debug:
        msg = "%.4f " * len(args) % args
        print(msg)
    else:
        msg = "%.4f " * len(args) % args
        try:
            sock.send(bytes(msg, "utf-8"))
        except socket.error as error:
            print(f"{str(error)}")
            sys.exit()


def test_with_mediapipe() -> None:
    """
    Uses mediapipe model for facial landmarks.
    """
    capt = cv2.VideoCapture(0)

    mesh_mediapipe = FaceMesh()

    cam_connected, img = capt.read()

    head_pose = HeadPose((img.shape[0], img.shape[1]))
    landmark_points = np.zeros((head_pose.model_points_full.shape[0], 2))
    iris_points = np.zeros((10, 2))

    pose_stabilizers = [HeadPoseStabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(6)]

    eyes_stabilizers = [HeadPoseStabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1) for _ in range(6)]

    mouth_dist_stabilizer = HeadPoseStabilizer(
        state_num=2,
        measure_num=1,
        cov_process=0.1,
        cov_measure=0.1
    )

    connected_socket = socket_connect()

    while capt.isOpened():
        cam_connected, img = capt.read()

        if not cam_connected:
            continue

        img_mesh, faces_detected = mesh_mediapipe.place_mesh(img)
        img = cv2.flip(img, 1)

        if faces_detected:
            for i in range(len(landmark_points)):
                landmark_points[i, 0] = faces_detected[0][i][0]
                landmark_points[i, 1] = faces_detected[0][i][1]
            for i in range(len(iris_points)):
                iris_points[i, 0] = faces_detected[0][i+468][0]
                iris_points[i, 1] = faces_detected[0][i+468][1]

            pose = head_pose.solve_pose(landmark_points)

            x_ratio_left, y_ratio_left = detect_iris(
                landmark_points, iris_points, 1)
            x_ratio_right, y_ratio_right = detect_iris(
                landmark_points, iris_points, 2)

            ear_left = eye_aspect_ratio(landmark_points, 1)
            ear_right = eye_aspect_ratio(landmark_points, 2)

            pose_eye = [
                ear_left,
                ear_right,
                x_ratio_left,
                y_ratio_left,
                x_ratio_right,
                y_ratio_right]

            mar = mouth_aspect_ratio(landmark_points)
            mouth_dist = mouth_distance(landmark_points)

            steady_pose = []
            pose_np = np.array(pose).flatten()

            for value, ps_stb in zip(pose_np, pose_stabilizers):
                ps_stb.update([value])
                steady_pose.append(ps_stb.state[0])

            steady_pose = np.reshape(steady_pose, (-1, 3))

            steady_pose_eye = []
            for value, ps_stb in zip(pose_eye, eyes_stabilizers):
                ps_stb.update([value])
                steady_pose_eye.append(ps_stb.state[0])

            mouth_dist_stabilizer.update([mouth_dist])

            roll = np.clip(np.degrees(steady_pose[0][1]), -90, 90)
            pitch = np.clip(180 + np.degrees(steady_pose[0][0]), -90, 90)
            yaw = np.clip(np.degrees(steady_pose[0][2]), -90, 90)

            socket_send(
                connected_socket, (
                    -roll,
                    -pitch,
                    -yaw,
                    ear_left,
                    ear_right,
                    x_ratio_left,
                    y_ratio_left,
                    x_ratio_right,
                    y_ratio_right,
                    mar,
                    mouth_dist
                )
            )

        else:
            head_pose = HeadPose((img_mesh.shape[0], img_mesh.shape[1]))

        cv2.imshow("Unity Chan", img_mesh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capt.release()


if __name__ == "__main__":
    test_with_mediapipe()
