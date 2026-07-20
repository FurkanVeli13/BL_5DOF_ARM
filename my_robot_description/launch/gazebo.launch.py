import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
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

    # Gazebo Ignition simülasyonunu (boş dünya ile) başlatıyoruz
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Robot State Publisher (Simülasyon zamanı aktif!)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True # Gazebo saatiyle senkronizasyon için kritik!
        }]
    )

    # Robotu Gazebo dünyasına ekleme (Spawning)
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_robot',
        arguments=[
            '-name', 'my_robot',
            '-topic', 'robot_description'
        ],
        output='screen'
    )

    # Gazebo <-> ROS 2 Köprüsü (Bridge)
    # Saat ve eklem durumlarını çift yönlü taşır
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            # Saat köprüsü (Gazebo -> ROS 2)
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Eklem durumları köprüsü (Gazebo -> ROS 2)
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        output='screen'
    )

    # RViz2 (Simülasyon zamanı aktif!)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}], # RViz'in zaman kaymasını önler
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        ros_gz_bridge,
        rviz
    ])
