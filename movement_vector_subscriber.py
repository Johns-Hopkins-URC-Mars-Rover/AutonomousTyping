import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

class MovementVectorSubscriber(Node):
    def __init__(self):
        super().__init__('movement_vector_subscriber') # creates a node with the name 'movement_vector_subscriber'
        # creates a subscriber that listens to messages of type Vector3 on the topic 'movement_vector'
        # The '10' is the queue size (QoS profile)
        self.subscription = self.create_subscription(
            Vector3,
            'movement_vector',
            self.movement_vector_callback,
            10
        )
        self.subscription  # prevent unused variable warning

    def movement_vector_callback(self, msg):
        # This callback function is called whenever a new message is received on the 'movement_vector' topic
        self.get_logger().info(f'Received Vectors -> X: {msg.x:.2f}, Y: {msg.y:.2f}, Z: {msg.z:.2f}')

        # Here you can add code to process the received movement vector and control the robot accordingly
        # e.g., pass msg.x, msg.y, msg.z to a function that controls the robot's movement

def main(args=None):
    rclpy.init(args=args) # Initialize the ROS 2 Python client library
    movement_vector_subscriber = MovementVectorSubscriber() # Create an instance of the MovementVectorSubscriber node

    rclpy.spin(movement_vector_subscriber) # Keep the node running to allow it to receive messages

    movement_vector_subscriber.destroy_node() # Clean up the node when done
    rclpy.shutdown() # Shutdown the ROS 2 client library

if __name__ == '__main__':
    main()