"""
ROS 2 Publisher Node for End-Effector Movement Vectors.

This script defines a ROS 2 node that broadcasts 3D translation vectors 
(X, Y, Z) to the 'movement_vector' topic. These vectors can be used by a 
subscriber node to command physical hardware, such as a robotic arm chassis.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

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
        # A queue size of 10 ensures up to 10 messages are buffered if the 
        # subscriber is temporarily unable to process them immediately.
        self.publisher_ = self.create_publisher(Vector3, 'movement_vector', 10)

    def send_movement_vector(self, x: float, y: float, z: float):
        """
        Constructs and publishes a Vector3 message with the provided coordinates.
        
        Args:
            x (float): The movement displacement along the X-axis (e.g., in meters).
            y (float): The movement displacement along the Y-axis (e.g., in meters).
            z (float): The movement displacement along the Z-axis (e.g., in meters).
        """
        # Initialize an empty Vector3 message object
        msg = Vector3()
        
        # Assign the positional arguments to the message properties
        # Forcing float() ensures ROS 2 doesn't throw a type error if passed an int
        msg.x = float(x)
        msg.y = float(y)
        msg.z = float(z)
        
        # Broadcast the message to the ROS 2 network
        self.publisher_.publish(msg)
        
        # Log the published data to the console for debugging and tracking
        self.get_logger().info(f'Publishing Vectors -> X: {msg.x:.2f}, Y: {msg.y:.2f}, Z: {msg.z:.2f}')


def main(args=None):
    """
    The main entry point for the node.
    
    Initializes ROS 2 communications, creates the node instance, demonstrates 
    a test publish, and spins the node to keep it alive.
    """
    rclpy.init(args=args) # Initialize the ROS 2 Python client library
    movement_vector_publisher = MovementVectorPublisher() # Create an instance of the MovementVectorPublisher node
    # Example usage: Publish a movement vector (you can replace these values with actual logic)
    movement_vector_publisher.send_movement_vector(1.0, 0.5, 0.0)
    rclpy.spin(movement_vector_publisher) # Keep the node running to allow it to publish messages
    movement_vector_publisher.destroy_node() # Clean up the node when done
    rclpy.shutdown() # Shutdown the ROS 2 client library

if __name__ == '__main__':
    main()
