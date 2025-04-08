#! /usr/bin/env python3

import tf.transformations as tf_trans
from geometry_msgs.msg import Point
import numpy as np

def inverse_transform_point(robot_point, translation, rotation):
    # 构造旋转矩阵
    rot_matrix = tf_trans.quaternion_matrix(rotation)

    # 构造平移矩阵
    trans_matrix = tf_trans.translation_matrix(translation)

    # 合并旋转和平移矩阵
    transform_matrix = tf_trans.concatenate_matrices(trans_matrix, rot_matrix)

    # 计算逆变换矩阵
    inverse_transform_matrix = tf_trans.inverse_matrix(transform_matrix)

    # 创建一个4x1的矩阵来表示点
    robot_point_vector = [robot_point[0], robot_point[1], robot_point[2], 1]

    # 应用逆变换
    transformed_vector = tf_trans.concatenate_matrices(inverse_transform_matrix, tf_trans.translation_matrix(robot_point_vector))
    camera_point = tf_trans.translation_from_matrix(transformed_vector)

    # 创建并返回新的点
    transformed_point = Point()
    transformed_point.x = camera_point[0]
    transformed_point.y = camera_point[1]
    transformed_point.z = camera_point[2]

    return transformed_point


def transform_point(point, translation, rotation):
    if point.z == 0:
        point = None
        return None
    else:    # 构造旋转矩阵
        rot_matrix = tf_trans.quaternion_matrix(rotation)

        # 构造平移矩阵
        trans_matrix = tf_trans.translation_matrix(translation)

        # 合并旋转和平移矩阵
        transform_matrix = tf_trans.concatenate_matrices(trans_matrix, rot_matrix)

        # 创建一个4x1的矩阵来表示点
        point_vector = [point.x, point.y, point.z, 1]

        # 应用变换
        transformed_vector = tf_trans.concatenate_matrices(transform_matrix, tf_trans.translation_matrix(point_vector))
        transformed_point = tf_trans.translation_from_matrix(transformed_vector)
        transformed_vector = np.dot(transform_matrix, point_vector)
        print(transformed_vector)
        transformed_point = transformed_vector[:3]
        return transformed_point[:3]  # 返回x, y, z坐标


# 提供的XYZ和四元数（从 camera_color_optical_frame 到 base_link 的变换）
translation = [0.381, 0.768, 1.365]  # XYZ
rotation = [0.776, 0.462, -0.299, 0.310]  # 四元数 (qx, qy, qz, qw)

# 定义相机坐标系中的点
#camera_point = Point(0.13915759076581277,0.12376043833590925,1.0190000000000001)
#camera_point = Point(0.14193078080704905, 0.21119500692479073, 0.984)
#camera_point = Point(-0.002467096769616618, 0.21343685243170551, 0.915)
#camera_point = Point(-0.001267003326396592, 0.28198187029565847, 0.792)
camera_point = Point(0.21962685837362217, 0.18346796411151925, 0.896)
#camera_point = Point(0.22747600205170845, 0.2374603920368252, 0.8150000000000001)
#camera_point = Point(-0.06604601024488924, 0.17966423854064217, 1.0130000000000001)
# 转换点
transformed_point = transform_point(camera_point, translation, rotation)
print(transformed_point)
camera_point2 = inverse_transform_point(transformed_point, translation, rotation)
print(camera_point2)
print("Transformed Point in base_link: (%.2f, %.2f, %.2f)", transformed_point[0], transformed_point[1], transformed_point[2])

print(transformed_point[1]/1.414 - transformed_point[0]/1.414)
print(transformed_point[1]/1.414 + transformed_point[0]/1.414)
