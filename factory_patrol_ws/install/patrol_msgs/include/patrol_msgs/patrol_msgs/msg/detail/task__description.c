// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/Task.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/task__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__Task__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xbd, 0xc9, 0x63, 0xbf, 0xe9, 0x48, 0x2d, 0xec,
      0xe1, 0x7e, 0x0a, 0x87, 0x97, 0xdb, 0x24, 0x84,
      0x45, 0x23, 0x8c, 0xee, 0x1e, 0x42, 0x7d, 0x3c,
      0x64, 0xb6, 0xe9, 0xbd, 0xc6, 0x5f, 0x8b, 0xb9,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__Task__TYPE_NAME[] = "patrol_msgs/msg/Task";

// Define type names, field names, and default values
static char patrol_msgs__msg__Task__FIELD_NAME__task_id[] = "task_id";
static char patrol_msgs__msg__Task__FIELD_NAME__x[] = "x";
static char patrol_msgs__msg__Task__FIELD_NAME__y[] = "y";
static char patrol_msgs__msg__Task__FIELD_NAME__z[] = "z";
static char patrol_msgs__msg__Task__FIELD_NAME__priority[] = "priority";
static char patrol_msgs__msg__Task__FIELD_NAME__inspection_type[] = "inspection_type";
static char patrol_msgs__msg__Task__FIELD_NAME__hover_duration[] = "hover_duration";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__Task__FIELDS[] = {
  {
    {patrol_msgs__msg__Task__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Task__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Task__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Task__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Task__FIELD_NAME__priority, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Task__FIELD_NAME__inspection_type, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Task__FIELD_NAME__hover_duration, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
patrol_msgs__msg__Task__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__Task__TYPE_NAME, 20, 20},
      {patrol_msgs__msg__Task__FIELDS, 7, 7},
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
  "float32 x\n"
  "float32 y\n"
  "float32 z\n"
  "uint8 priority\n"
  "uint8 inspection_type\n"
  "float32 hover_duration";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__Task__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__Task__TYPE_NAME, 20, 20},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 105, 105},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__Task__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__Task__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
