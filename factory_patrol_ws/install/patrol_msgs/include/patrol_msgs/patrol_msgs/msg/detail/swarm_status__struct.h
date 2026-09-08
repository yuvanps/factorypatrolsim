// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/swarm_status.h"


#ifndef PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'STATUS_OK'.
enum
{
  patrol_msgs__msg__SwarmStatus__STATUS_OK = 0
};

/// Constant 'STATUS_NO_DRONES_AVAILABLE'.
enum
{
  patrol_msgs__msg__SwarmStatus__STATUS_NO_DRONES_AVAILABLE = 1
};

/// Constant 'STATUS_ALL_DRONES_LOW_BATTERY'.
enum
{
  patrol_msgs__msg__SwarmStatus__STATUS_ALL_DRONES_LOW_BATTERY = 2
};

/// Constant 'STATUS_PATROL_CYCLE_COMPLETE'.
enum
{
  patrol_msgs__msg__SwarmStatus__STATUS_PATROL_CYCLE_COMPLETE = 3
};

// Include directives for member types
// Member 'reason'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/SwarmStatus in the package patrol_msgs.
typedef struct patrol_msgs__msg__SwarmStatus
{
  uint8_t status;
  rosidl_runtime_c__String reason;
} patrol_msgs__msg__SwarmStatus;

// Struct for a sequence of patrol_msgs__msg__SwarmStatus.
typedef struct patrol_msgs__msg__SwarmStatus__Sequence
{
  patrol_msgs__msg__SwarmStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__SwarmStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__STRUCT_H_
