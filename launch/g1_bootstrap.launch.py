import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_path = get_package_share_directory("fast_lio_ros2")
    default_config_path = os.path.join(package_path, "config")
    default_rviz_config_path = os.path.join(package_path, "rviz", "fastlio.rviz")

    use_sim_time = LaunchConfiguration("use_sim_time")
    namespace = LaunchConfiguration("namespace")
    config_path = LaunchConfiguration("config_path")
    config_file = LaunchConfiguration("config_file")
    rviz_use = LaunchConfiguration("rviz")
    rviz_cfg = LaunchConfiguration("rviz_cfg")
    robot_tf_use = LaunchConfiguration("robot_tf")
    joint_state_source = LaunchConfiguration("joint_state_source")
    joint_states_topic = LaunchConfiguration("joint_states_topic")
    lowstate_topic = LaunchConfiguration("lowstate_topic")
    unitree_message_type = LaunchConfiguration("unitree_message_type")
    unitree_dds_domain_id = LaunchConfiguration("unitree_dds_domain_id")
    unitree_network_interface = LaunchConfiguration("unitree_network_interface")
    joint_to_motor_indices = LaunchConfiguration("joint_to_motor_indices")
    state_estimation_topic = LaunchConfiguration("state_estimation_topic")

    map_frame_id = LaunchConfiguration("map_frame_id")
    odom_frame_id = LaunchConfiguration("odom_frame_id")
    initial_camera_frame_id = LaunchConfiguration("initial_camera_frame_id")
    left_foot_frame_id = LaunchConfiguration("left_foot_frame_id")
    right_foot_frame_id = LaunchConfiguration("right_foot_frame_id")
    height_mode = LaunchConfiguration("height_mode")
    map_to_odom_z_sign = LaunchConfiguration("map_to_odom_z_sign")
    map_to_odom_roll = LaunchConfiguration("map_to_odom_roll")
    map_to_odom_pitch = LaunchConfiguration("map_to_odom_pitch")
    map_to_odom_yaw = LaunchConfiguration("map_to_odom_yaw")
    fallback_initial_z = LaunchConfiguration("fallback_initial_z")

    robot_tf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("holosoma_robot_description"),
                "launch",
                "g1_robot_state_publisher.launch.py",
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "joint_state_source": joint_state_source,
            "joint_states_topic": joint_states_topic,
            "lowstate_topic": lowstate_topic,
            "unitree_message_type": unitree_message_type,
            "unitree_dds_domain_id": unitree_dds_domain_id,
            "unitree_network_interface": unitree_network_interface,
            "joint_to_motor_indices": joint_to_motor_indices,
            "publish_frequency": "200.0",
        }.items(),
        condition=IfCondition(robot_tf_use),
    )

    map_bootstrap_node = Node(
        package="holosoma_robot_description",
        executable="initial_map_frame_bootstrap",
        name="initial_map_frame_bootstrap",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "map_frame_id": map_frame_id,
                "odom_frame_id": odom_frame_id,
                "initial_camera_frame_id": initial_camera_frame_id,
                "left_foot_frame_id": left_foot_frame_id,
                "right_foot_frame_id": right_foot_frame_id,
                "height_mode": height_mode,
                "map_to_odom_z_sign": ParameterValue(map_to_odom_z_sign, value_type=float),
                "map_to_odom_roll": ParameterValue(map_to_odom_roll, value_type=float),
                "map_to_odom_pitch": ParameterValue(map_to_odom_pitch, value_type=float),
                "map_to_odom_yaw": ParameterValue(map_to_odom_yaw, value_type=float),
                "fallback_initial_z": ParameterValue(fallback_initial_z, value_type=float),
            }
        ],
    )

    fast_lio_node = Node(
        package="fast_lio_ros2",
        executable="fastlio_ros2_mapping",
        namespace=namespace,
        name="laser_mapping",
        output="screen",
        parameters=[
            PathJoinSubstitution([config_path, config_file]),
            {
                "use_sim_time": use_sim_time,
            },
        ],
        remappings=[
            ("Odometry", state_estimation_topic),
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_cfg, "--ros-args", "--log-level", "warn"],
        output="screen",
        condition=IfCondition(rviz_use),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument("namespace", default_value="fast_lio_ros2"),
            DeclareLaunchArgument("config_path", default_value=default_config_path),
            DeclareLaunchArgument("config_file", default_value="g1_bootstrap.yaml"),
            DeclareLaunchArgument("rviz", default_value="false"),
            DeclareLaunchArgument("rviz_cfg", default_value=default_rviz_config_path),
            DeclareLaunchArgument("robot_tf", default_value="true"),
            DeclareLaunchArgument("joint_state_source", default_value="dummy"),
            DeclareLaunchArgument("joint_states_topic", default_value="/joint_states"),
            DeclareLaunchArgument("lowstate_topic", default_value="rt/lowstate"),
            DeclareLaunchArgument("unitree_message_type", default_value="hg"),
            DeclareLaunchArgument("unitree_dds_domain_id", default_value="0"),
            DeclareLaunchArgument("unitree_network_interface", default_value=""),
            DeclareLaunchArgument("joint_to_motor_indices", default_value=""),
            DeclareLaunchArgument("state_estimation_topic", default_value="/state_estimation"),
            DeclareLaunchArgument("map_frame_id", default_value="map"),
            DeclareLaunchArgument("odom_frame_id", default_value="odom"),
            DeclareLaunchArgument("initial_camera_frame_id", default_value="mid360_link"),
            DeclareLaunchArgument("left_foot_frame_id", default_value="LL_FOOT"),
            DeclareLaunchArgument("right_foot_frame_id", default_value="LR_FOOT"),
            DeclareLaunchArgument("height_mode", default_value="average_abs_z"),
            DeclareLaunchArgument("map_to_odom_z_sign", default_value="1.0"),
            DeclareLaunchArgument("map_to_odom_roll", default_value="0.0"),
            DeclareLaunchArgument("map_to_odom_pitch", default_value="0.0"),
            DeclareLaunchArgument("map_to_odom_yaw", default_value="0.0"),
            DeclareLaunchArgument("fallback_initial_z", default_value="0.0"),
            robot_tf_launch,
            map_bootstrap_node,
            TimerAction(period=1.0, actions=[fast_lio_node]),
            rviz_node,
        ]
    )
