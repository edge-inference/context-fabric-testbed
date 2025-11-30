from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration

def launch_setup(context, *args, **kwargs):
    device_id_str = LaunchConfiguration('device_id').perform(context)
    device_id = int(device_id_str)
    
    mode_str = LaunchConfiguration('mode').perform(context)
    
    nodes = []
    
    # 1. Start Coordinator Node (Control Plane - One per device)
    if mode_str == 'lf':
        # LF Federated Mode: Start ROS-LF bridge
        nodes.append(Node(
            package='coord',
            executable='lf_bridge_node',
            name=f'lf_bridge_{device_id}',
            parameters=[{
                'device_id': device_id,
                'lf_port': 9000 + device_id  # Fed1=9001, Fed2=9002
            }],
            output='screen'
        ))
    else:
        # ZooKeeper Mode: Standard coordinator
        nodes.append(Node(
            package='coord',
            executable='coord_node',
            name=f'coordinator_{device_id}',
            parameters=[{
                'lease_ttl_ms': 300000,
                'tick_rate_ms': 100
            }]
        ))
    
    # 2. Start DSM Node (Data Plane - One per device)
    nodes.append(Node(
        package='dsm',
        executable='dsm_node',
        name=f'dsm_node_{device_id}',
        parameters=[{'device_id': device_id}]
    ))
    
    # 3. Start Agent Node (One per device/robot)
    # Device ID = Robot ID = Agent ID
    nodes.append(Node(
        package='agent',
        executable='agent_node',
        name=f'agent_{device_id}',
        parameters=[{
            'agent_id': device_id,
            'device_id': device_id,
            'start_node': 0
        }],
        output='screen'
    ))

    return nodes

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'device_id',
            default_value='1',
            description='Unique ID for this physical device (integer)'
        ),
        DeclareLaunchArgument(
            'mode',
            default_value='zookeeper',
            description='Coordination mode: "zookeeper" (standard) or "lf" (federated deterministic)'
        ),
        OpaqueFunction(function=launch_setup)
    ])
