import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Paket dizinini alıyoruz
    pkg_share = get_package_share_directory('my_robot_description')
    
    # URDF ve RViz dosyalarının yolları
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.urdf')
    rviz_config = os.path.join(pkg_share, 'rviz', 'model.rviz')

    # URDF içeriğini okuyoruz
    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    return LaunchDescription([
        # 1. Robot State Publisher: URDF'i okur ve TF koordinatlarını yayınlar
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]            
        ),

        # 2. Joint State Publisher GUI: Eklemleri kaydırıcılarla manuel hareket ettirir
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # 3. RViz2: Robotu kaydettiğin model.rviz ayarlarıyla açar
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]
        )
    ])
