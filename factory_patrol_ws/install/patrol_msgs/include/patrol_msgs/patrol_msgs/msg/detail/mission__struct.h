// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/Mission.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/mission.h"


#ifndef PATROL_MSGS__MSG__DETAIL__MISSION__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__MISSION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'tasks'
#include "patrol_msgs/msg/detail/task__struct.h"

/// Struct defined in msg/Mission in the package patrol_msgs.
typedef struct patrol_msgs__msg__Mission
{
  uint16_t mission_id;
  patrol_msgs__msg__Task__Sequence tasks;
} patrol_msgs__msg__Mission;

// Struct for a sequence of patrol_msgs__msg__Mission.
typedef struct patrol_msgs__msg__Mission__Sequence
{
  patrol_msgs__msg__Mission * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__Mission__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__MISSION__STRUCT_H_
