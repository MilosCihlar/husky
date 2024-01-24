import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    velocity_controller = LaunchConfiguration('velocity_controller')
    velocity_controller_cmd = DeclareLaunchArgument(
                                    'velocity_controller',
                                    description='Config yaml file for husky velocity controller.')

    config_path = os.path.join(FindPackageShare(package='models').find('models'), 'ugvs/' + os.environ['UGV_NAME'] + '/config/' + os.environ['UGV_SENSORS'] + '.yaml')

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("models"), "ugvs/husky/", "husky.xacro"]
            ),
            " ",
            "namespace:=" + os.environ['UGV_NAME'] + "_" + os.environ['UGV_NUMBER'],
            " ",
            "is_sim:=False",
            " ",
            "accessories:=" + os.environ['UGV_ACCESSORIES'],
            " ",
            "sensor_config_path:=" + config_path,
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        namespace=[os.environ['UGV_NAME'], '_', os.environ['UGV_NUMBER'], '/chassis'],
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    node_controller_manager = Node(
        package="controller_manager",
        namespace=[os.environ['UGV_NAME'], '_', os.environ['UGV_NUMBER'], '/chassis'],
        executable="ros2_control_node",
        remappings=[('husky_velocity_controller/cmd_vel_unstamped', 'cmd_vel'),
                    ('husky_velocity_controller/odom','odometry'),
                    ('husky_velocity_controller/odom','odometry'),
                    ],
        parameters=[robot_description, velocity_controller],
        output={
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    spawn_controller = Node(
        package="controller_manager",
        namespace=[os.environ['UGV_NAME'], '_', os.environ['UGV_NUMBER'], '/chassis'],
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    spawn_husky_velocity_controller = Node(
        package="controller_manager",
        namespace=[os.environ['UGV_NAME'], '_', os.environ['UGV_NUMBER'], '/chassis'],
        executable="spawner",
        arguments=["husky_velocity_controller"],
        output="screen",
    )

    ld = LaunchDescription()
    ld.add_action(velocity_controller_cmd)

    ld.add_action(node_robot_state_publisher)
    ld.add_action(node_controller_manager)
    ld.add_action(spawn_controller)
    ld.add_action(spawn_husky_velocity_controller)

    return ld
