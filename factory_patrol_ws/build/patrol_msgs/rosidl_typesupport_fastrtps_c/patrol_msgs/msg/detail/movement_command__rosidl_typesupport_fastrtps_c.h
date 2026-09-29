// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from patrol_msgs:msg/MovementCommand.idl
// generated code does not contain a copyright notice
#ifndef PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "patrol_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "patrol_msgs/msg/detail/movement_command__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
bool cdr_serialize_patrol_msgs__msg__MovementCommand(
  const patrol_msgs__msg__MovementCommand * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
bool cdr_deserialize_patrol_msgs__msg__MovementCommand(
  eprosima::fastcdr::Cdr &,
  patrol_msgs__msg__MovementCommand * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
size_t get_serialized_size_patrol_msgs__msg__MovementCommand(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
size_t max_serialized_size_patrol_msgs__msg__MovementCommand(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
bool cdr_serialize_key_patrol_msgs__msg__MovementCommand(
  const patrol_msgs__msg__MovementCommand * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
size_t get_serialized_size_key_patrol_msgs__msg__MovementCommand(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
size_t max_serialized_size_key_patrol_msgs__msg__MovementCommand(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_patrol_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, patrol_msgs, msg, MovementCommand)();

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
