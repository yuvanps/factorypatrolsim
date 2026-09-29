// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/DroneState.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/drone_state.h"


#ifndef PATROL_MSGS__MSG__DETAIL__DRONE_STATE__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__DRONE_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/DroneState in the package patrol_msgs.
typedef struct patrol_msgs__msg__DroneState
{
  uint8_t drone_id;
  float x;
  float y;
  float z;
  float battery_level;
  uint8_t state;
  /// task the drone is currently flying to / inspecting (0 = none)
  uint16_t current_task_id;
} patrol_msgs__msg__DroneState;

// Struct for a sequence of patrol_msgs__msg__DroneState.
typedef struct patrol_msgs__msg__DroneState__Sequence
{
  patrol_msgs__msg__DroneState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__DroneState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__DRONE_STATE__STRUCT_H_
