class Robot(object):

    def set_tcp_pose(self, target_pose):
        """Move the tool center point to the given pose.

        Args:
            target_pose: The target pose of the TCP in body frame, T_body_tcp.
        """
        raise NotImplementedError

    def move_tcp_xyz(self, target_pose, eef_step):
        """Linearly move the EE in cartesian space to the given pose.

        Args:
            target_pose: The target pose of the TCP in body frame.
            eef_step: Path interpolation resolution [m].
        """
        raise NotImplementedError

    def open_gripper(self):
        """Open the gripper."""
        raise NotImplementedError

    def close_gripper(self):
        """Close the gripper."""
        raise NotImplementedError