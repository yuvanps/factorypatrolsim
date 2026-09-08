cmake_minimum_required(VERSION 3.8)

project(patrol_controller C)

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

find_package(ament_cmake REQUIRED)
find_package(rcl REQUIRED)
find_package(rclc REQUIRED)
find_package(px4_msgs REQUIRED)
find_package(patrol_msgs REQUIRED)

include_directories(include)

add_executable(patrol_controller
  src/patrol_controller.c
  src/auction_logic.c
)

target_link_libraries(patrol_controller
  m
)

ament_target_dependencies(patrol_controller
  rcl
  rclc
  px4_msgs
  patrol_msgs
)

install(
  TARGETS patrol_controller
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

























