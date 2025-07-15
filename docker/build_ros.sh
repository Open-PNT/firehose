#!/bin/bash

source /opt/ros/$ROS_DISTRO/setup.bash
mkdir -p ~/ros_ws/src /output/ros_devel/$ROS_DISTRO
cd ~/ros_ws
cp -r /output/aspn-ros src
colcon build
cd install
shopt -s globstar
clang-format -i -- **/*.c **/*.h **/*.cpp **/*.hpp
cp -r ./* /output/ros_devel/$ROS_DISTRO
