import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

class MovementVectorPublisher(Node):
    def __init__(self):
        super().__init__('movement_vector_publisher') # creates a node with the name 'movement_vector_publisher'
        # creates a publisher that will publish messages of type Vector3 to the topic 'movement_vector' 
        # The '10' is the queue size (QoS profile)
        self.publisher_ = self.create_publisher(Vector3, 'movement_vector', 10)

    def send_movement_vector(self, x, y, z):
        # Create a Vector3 message and set its x, y, z components
        msg = Vector3()
        msg.x = x
        msg.y = y
        msg.z = z
        # Publish the message to the topic
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing Vectors -> X: {msg.x:.2f}, Y: {msg.y:.2f}, Z: {msg.z:.2f}')

def main(args=None):
    rclpy.init(args=args) # Initialize the ROS 2 Python client library
    movement_vector_publisher = MovementVectorPublisher() # Create an instance of the MovementVectorPublisher node
    # Example usage: Publish a movement vector (you can replace these values with actual logic)
    movement_vector_publisher.send_movement_vector(1.0, 0.5, 0.0)
    rclpy.spin(movement_vector_publisher) # Keep the node running to allow it to publish messages

    movement_vector_publisher.destroy_node() # Clean up the node when done
    rclpy.shutdown() # Shutdown the ROS 2 client library

if __name__ == '__main__':
    main()