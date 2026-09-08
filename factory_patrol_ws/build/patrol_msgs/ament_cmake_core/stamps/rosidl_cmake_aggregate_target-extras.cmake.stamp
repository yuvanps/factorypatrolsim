# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target patrol_msgs::patrol_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${patrol_msgs_TARGETS}.
if(patrol_msgs_TARGETS AND NOT TARGET patrol_msgs::patrol_msgs)
  add_library(patrol_msgs::patrol_msgs INTERFACE IMPORTED)
  set_target_properties(patrol_msgs::patrol_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${patrol_msgs_TARGETS}")
endif()
