"""
ROS 2 Publisher Node for End-Effector Movement Vectors.

This script defines a ROS 2 node that broadcasts 3D translation vectors 
(X, Y, Z) to the 'movement_vector' topic. These vectors can be used by a 
subscriber node to command physical hardware, such as a robotic arm chassis.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String

class MovementVectorPublisher(Node):
    """
    A custom ROS 2 node class that publishes geometry_msgs/Vector3 messages.
    
    Inherits from:
        rclpy.node.Node
    """

    def __init__(self):
        """
        Initializes the MovementVectorPublisher node.
        
        Sets the node name to 'movement_vector_publisher' and creates a 
        publisher for the 'movement_vector' topic with a queue size of 10.
        """
        super().__init__('movement_vector_publisher')
        
        # Create a publisher for Vector3 messages on the 'movement_vector' topic.
        self.publisher_ = self.create_publisher(Vector3, 'movement_vector', 10)
        self.publisher_completion = self.create_publisher(String, 'Completion', 10)

    def send_movement_vector(self, x: float, y: float, z: float):
        """
        Constructs and publishes a Vector3 message with the provided coordinates.
        
        Args:
            x (float): The movement displacement along the X-axis (e.g., in meters).
            y (float): The movement displacement along the Y-axis (e.g., in meters).
            z (float): The movement displacement along the Z-axis (e.g., in meters).
        """
        msg = Vector3()
        
        # Assign the positional arguments to the message properties
        msg.x = float(x)
        msg.y = float(y)
        msg.z = float(z)
        
        # Broadcast the message to the ROS 2 network
        self.publisher_.publish(msg)
        
        # Log the published data to the console for debugging and tracking
        self.get_logger().info(f'Publishing Vectors -> X: {msg.x:.2f}, Y: {msg.y:.2f}, Z: {msg.z:.2f}')
    
    def send_completion_message(self, message: str):
        """
        Constructs and publishes a String message indicating task completion.
        
        Args:
            message (str): A human-readable string indicating the status or 
                           completion of a task (e.g., "Task Completed").
        """
        msg = String()
        msg.data = message
        self.publisher_completion.publish(msg)
        
        # Log the published completion message to the console for debugging
        self.get_logger().info(f'Publishing Completion Message -> {msg.data}')


def main(args=None):
    """
    The main entry point for the node.
    
    Initializes ROS 2 communications, creates the node instance, demonstrates 
    a test publish, and spins the node to keep it alive.
    """
    rclpy.init(args=args)
    movement_vector_publisher = MovementVectorPublisher()
    movement_vector_publisher.send_movement_vector(1.0, 0.5, 0.0)
    rclpy.spin(movement_vector_publisher)
    movement_vector_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
