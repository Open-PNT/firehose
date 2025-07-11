from typing import Type, Callable, Optional

from rclpy.node import Node, Subscription
from rclpy.publisher import Publisher
from rosidl_runtime_py.utilities import get_message

from aspn23_ros_utils.ros_translations import (
    AspnMsg,
    RosMsg,
    from_ros_map,
    to_ros_map,
)
import aspn23_ros_interfaces.msg as ros_msg


class AspnRosNode(Node):
    def __init__(self, node_name: str, queue_size: int = 100):
        super().__init__(node_name)
        self.queue_size = queue_size
        self.pubs: dict[str, Publisher] = {}

    def subscribe_aspn(
        self,
        aspn_cb: Callable[[AspnMsg], None],
        topic: str,
        msg_type: Optional[Type[AspnMsg]] = None,
    ) -> Subscription:
        ros_msg_type = None
        if msg_type is not None:
            ros_msg_type = getattr(ros_msg, msg_type.__name__)

        def ros_cb(ros_msg: RosMsg):
            aspn_cb(from_ros_map[type(ros_msg)](ros_msg))

        return self.subscribe_ros(ros_cb, topic, ros_msg_type)

    def subscribe_ros(
        self,
        ros_cb: Callable[[RosMsg], None],
        topic: str,
        msg_type: Optional[Type[RosMsg]] = None,
    ) -> Subscription:
        if msg_type is None:
            try:
                msg_type = get_message(
                    dict(self.get_topic_names_and_types())[topic][0]
                )
            except KeyError:
                raise RuntimeError(
                    f"Trying to deduce message type from topic '{topic}', but "
                    f"it doesn't exist yet... Can't speculatively subscribe "
                    f"unless message type is specified."
                )
        self.get_logger().info(f"Subscribing to '{topic}'.")
        return self.create_subscription(
            msg_type, topic, ros_cb, self.queue_size
        )

    def publish_aspn(self, aspn_msg: AspnMsg, topic: str) -> None:
        self.publish_ros(to_ros_map[type(aspn_msg)](aspn_msg), topic)

    def publish_ros(self, ros_msg: RosMsg, topic: str) -> None:
        if topic not in self.pubs:
            self.pubs[topic] = self.create_publisher(
                type(ros_msg), topic, self.queue_size
            )
        self.pubs[topic].publish(ros_msg)
        self.get_logger().info(f"Published on '{topic}'.")
