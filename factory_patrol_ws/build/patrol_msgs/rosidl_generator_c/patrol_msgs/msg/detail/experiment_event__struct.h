// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from patrol_msgs:msg/ExperimentEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/experiment_event.h"


#ifndef PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__STRUCT_H_
#define PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'event_type'
// Member 'data'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/ExperimentEvent in the package patrol_msgs.
typedef struct patrol_msgs__msg__ExperimentEvent
{
  uint64_t timestamp;
  rosidl_runtime_c__String event_type;
  rosidl_runtime_c__String data;
} patrol_msgs__msg__ExperimentEvent;

// Struct for a sequence of patrol_msgs__msg__ExperimentEvent.
typedef struct patrol_msgs__msg__ExperimentEvent__Sequence
{
  patrol_msgs__msg__ExperimentEvent * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} patrol_msgs__msg__ExperimentEvent__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__STRUCT_H_
