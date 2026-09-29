// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/MovementCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/movement_command.h"


#ifndef PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/MovementCommand in the package patrol_msgs.
/**
  * Movement command from a reactive coordination algorithm (e.g. APF) to one patrol controller.
  * All positions/velocities are in the common factory frame used by DroneState and Task:
  *   x = Gazebo X (east), y = Gazebo Y (north), z = -height (negative = above ground).
 */
typedef struct patrol_msgs__msg__MovementCommand
{
  uint8_t drone_id;
  /// goal this command steers toward; controllers ignore commands for any other task
  uint16_t task_id;
  /// position setpoint the controller should track
  float target_x;
  float target_y;
  float target_z;
  /// commanded velocity that produced the target (informational / diagnostics)
  float velocity_x;
  float velocity_y;
  float velocity_z;
} patrol_msgs__msg__MovementCommand;

// Struct for a sequence of patrol_msgs__msg__MovementCommand.
typedef struct patrol_msgs__msg__MovementCommand__Sequence
{
  patrol_msgs__msg__MovementCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__MovementCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__STRUCT_H_
