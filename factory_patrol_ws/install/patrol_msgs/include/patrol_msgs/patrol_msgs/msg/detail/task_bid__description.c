// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/task_bid__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__TaskBid__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x18, 0x54, 0xb4, 0xd0, 0xc3, 0x2c, 0x43, 0x3a,
      0xc4, 0xce, 0x37, 0x43, 0x3e, 0xe6, 0x1a, 0x96,
      0x75, 0xe5, 0x88, 0xb0, 0x1b, 0x2b, 0xa9, 0x12,
      0x29, 0x08, 0x7a, 0xde, 0x6e, 0xe1, 0xf6, 0xba,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char patrol_msgs__msg__TaskBid__TYPE_NAME[] = "patrol_msgs/msg/TaskBid";

// Define type names, field names, and default values
static char patrol_msgs__msg__TaskBid__FIELD_NAME__drone_id[] = "drone_id";
static char patrol_msgs__msg__TaskBid__FIELD_NAME__task_id[] = "task_id";
static char patrol_msgs__msg__TaskBid__FIELD_NAME__cost[] = "cost";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__TaskBid__FIELDS[] = {
  {
    {patrol_msgs__msg__TaskBid__FIELD_NAME__drone_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__TaskBid__FIELD_NAME__task_id, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__TaskBid__FIELD_NAME__cost, 4, 4},
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
patrol_msgs__msg__TaskBid__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__TaskBid__TYPE_NAME, 23, 23},
      {patrol_msgs__msg__TaskBid__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 drone_id\n"
  "uint16 task_id\n"
  "float32 cost";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__TaskBid__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__TaskBid__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 43, 43},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__TaskBid__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__TaskBid__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
