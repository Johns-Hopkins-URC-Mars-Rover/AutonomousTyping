"""
ROS 2 Subscriber Node for End-Effector Movement Vectors.

This script defines a ROS 2 node that listens to the 'movement_vector' topic
for 3D translation vectors (X, Y, Z). Upon receiving a message, it triggers
a callback function where the physical hardware control logic (e.g., PID 
controllers for a robotic arm or rover chassis) should be implemented.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String

class MovementVectorSubscriber(Node):
    """
    A custom ROS 2 node class that subscribes to geometry_msgs/Vector3 messages.
    
    Inherits from:
        rclpy.node.Node
    """

    def __init__(self):
        """
        Initializes the MovementVectorSubscriber node.
        
        Sets the node name to 'movement_vector_subscriber' and creates a 
        subscription to the 'movement_vector' topic with a queue size of 10.
        """
        super().__init__('movement_vector_subscriber')
        
        # Create a subscriber for Vector3 messages on the 'movement_vector' topic.
        # The queue size of 10 determines how many incoming messages are buffered 
        # if the callback function is momentarily busy processing a previous message.
        self.subscription = self.create_subscription(
            Vector3,
            'movement_vector',
            self.movement_vector_callback,
            10
        )
        self.subscription = self.create_subscription(
            String,
            'Completion',
            self.completion_callback,
            10
        )

        # Prevent the Python garbage collector from destroying the subscription 
        # by explicitly referencing it (a standard ROS 2 Python convention).
        self.subscription

    def movement_vector_callback(self, msg: Vector3):
        """
        Callback function triggered automatically whenever a new message arrives.
        
        Args:
            msg (geometry_msgs.msg.Vector3): The incoming movement vector containing 
                                             x, y, and z float components.
        """
        # Log the received data to the console for monitoring and debugging
        self.get_logger().info(f'Received Vectors -> X: {msg.x:.2f}, Y: {msg.y:.2f}, Z: {msg.z:.2f}')

        # -------------------------------------------------------------------
        # HARDWARE CONTROL LOGIC GOES HERE
        # -------------------------------------------------------------------
        # Example Implementation Steps:
        # 1. Pass msg.x, msg.y, and msg.z into your PID controllers.
        # 2. Convert the PID output into motor commands (e.g., PWM or velocities).
        # 3. Send those commands to the physical robot joints/wheels.
        # -------------------------------------------------------------------

    def completion_callback(self, msg: String):
        """Callback function triggered when a completion message is received.

        Args:
            msg (std_msgs.msg.String): The incoming completion message.
        """
        self.get_logger().info(f'Received Completion Message: {msg.data}')
        return True
        
def main(args=None):
    """
    The main entry point for the node.
    
    Initializes ROS 2 communications, creates the subscriber instance, and 
    spins the node indefinitely so it continuously listens for incoming data.
    """
    rclpy.init(args=args) # Initialize the ROS 2 Python client library
    movement_vector_subscriber = MovementVectorSubscriber() # Create an instance of the MovementVectorSubscriber node
    rclpy.spin(movement_vector_subscriber) # Keep the node running to allow it to receive messages
    movement_vector_subscriber.destroy_node() # Clean up the node when done
    rclpy.shutdown() # Shutdown the ROS 2 client library

if __name__ == '__main__':
    main()
