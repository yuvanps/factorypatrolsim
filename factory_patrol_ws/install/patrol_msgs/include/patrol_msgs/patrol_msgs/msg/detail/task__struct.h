// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/Task.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task.h"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__TASK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/Task in the package patrol_msgs.
typedef struct patrol_msgs__msg__Task
{
  uint16_t task_id;
  float x;
  float y;
  float z;
  uint8_t priority;
  uint8_t inspection_type;
  float hover_duration;
} patrol_msgs__msg__Task;

// Struct for a sequence of patrol_msgs__msg__Task.
typedef struct patrol_msgs__msg__Task__Sequence
{
  patrol_msgs__msg__Task * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__Task__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__TASK__STRUCT_H_
