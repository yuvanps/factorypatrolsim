// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/TaskAssignment.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/task_assignment__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__TaskAssignment__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x41, 0x8f, 0x95, 0xe7, 0x3e, 0xea, 0xad, 0x25,
      0x55, 0xf3, 0xe7, 0x38, 0xe8, 0x73, 0x15, 0xc8,
      0x98, 0xa2, 0x94, 0x66, 0x16, 0x48, 0x06, 0xb9,
      0xc9, 0x84, 0xab, 0x23, 0x36, 0xfb, 0xf9, 0x1b,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__TaskAssignment__TYPE_NAME[] = "patrol_msgs/msg/TaskAssignment";

// Define type names, field names, and default values
static char patrol_msgs__msg__TaskAssignment__FIELD_NAME__task_id[] = "task_id";
static char patrol_msgs__msg__TaskAssignment__FIELD_NAME__drone_id[] = "drone_id";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__TaskAssignment__FIELDS[] = {
  {
    {patrol_msgs__msg__TaskAssignment__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__TaskAssignment__FIELD_NAME__drone_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
patrol_msgs__msg__TaskAssignment__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__TaskAssignment__TYPE_NAME, 30, 30},
      {patrol_msgs__msg__TaskAssignment__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint16 task_id\n"
  "uint8 drone_id";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__TaskAssignment__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__TaskAssignment__TYPE_NAME, 30, 30},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 30, 30},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__TaskAssignment__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__TaskAssignment__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
