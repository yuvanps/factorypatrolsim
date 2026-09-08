// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task_bid.h"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK_BID__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__TASK_BID__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/TaskBid in the package patrol_msgs.
typedef struct patrol_msgs__msg__TaskBid
{
  uint8_t drone_id;
  uint16_t task_id;
  float cost;
} patrol_msgs__msg__TaskBid;

// Struct for a sequence of patrol_msgs__msg__TaskBid.
typedef struct patrol_msgs__msg__TaskBid__Sequence
{
  patrol_msgs__msg__TaskBid * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__TaskBid__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__TASK_BID__STRUCT_H_
