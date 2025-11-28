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
    
    # 3. Start Agents with unique IDs derived from device_id
    # Example: Device 1 -> Agents 10, 11
    #          Device 2 -> Agents 20, 21
    base_id = device_id * 10
    agents_per_device = 2
    
    for i in range(agents_per_device):
        agent_id = base_id + i
        nodes.append(Node(
            package='agent',
            executable='agent_node',
            name=f'agent_{agent_id}',
            parameters=[{
                'agent_id': agent_id,
                'start_node': 0
            }]
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
