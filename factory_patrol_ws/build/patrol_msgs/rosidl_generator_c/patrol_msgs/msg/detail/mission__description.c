// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from patrol_msgs:msg/Mission.idl
// generated code does not contain a copyright notice

#include "patrol_msgs/msg/detail/mission__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_patrol_msgs
const rosidl_type_hash_t *
patrol_msgs__msg__Mission__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x48, 0xf8, 0x31, 0x8a, 0x38, 0xa3, 0x5c, 0x19,
      0x90, 0xf8, 0xab, 0xe2, 0x95, 0xac, 0x39, 0x30,
      0xf0, 0x90, 0xd5, 0xa0, 0xa2, 0xea, 0x02, 0xfa,
      0x32, 0xe4, 0x52, 0x9f, 0xde, 0x00, 0xa7, 0x99,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "patrol_msgs/msg/detail/task__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t patrol_msgs__msg__Task__EXPECTED_HASH = {1, {
    0xbd, 0xc9, 0x63, 0xbf, 0xe9, 0x48, 0x2d, 0xec,
    0xe1, 0x7e, 0x0a, 0x87, 0x97, 0xdb, 0x24, 0x84,
    0x45, 0x23, 0x8c, 0xee, 0x1e, 0x42, 0x7d, 0x3c,
    0x64, 0xb6, 0xe9, 0xbd, 0xc6, 0x5f, 0x8b, 0xb9,
  }};
#endif

static char patrol_msgs__msg__Mission__TYPE_NAME[] = "patrol_msgs/msg/Mission";
static char patrol_msgs__msg__Task__TYPE_NAME[] = "patrol_msgs/msg/Task";

// Define type names, field names, and default values
static char patrol_msgs__msg__Mission__FIELD_NAME__mission_id[] = "mission_id";
static char patrol_msgs__msg__Mission__FIELD_NAME__tasks[] = "tasks";

static rosidl_runtime_c__type_description__Field patrol_msgs__msg__Mission__FIELDS[] = {
  {
    {patrol_msgs__msg__Mission__FIELD_NAME__mission_id, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {patrol_msgs__msg__Mission__FIELD_NAME__tasks, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {patrol_msgs__msg__Task__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription patrol_msgs__msg__Mission__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {patrol_msgs__msg__Task__TYPE_NAME, 20, 20},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
patrol_msgs__msg__Mission__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {patrol_msgs__msg__Mission__TYPE_NAME, 23, 23},
      {patrol_msgs__msg__Mission__FIELDS, 2, 2},
    },
    {patrol_msgs__msg__Mission__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&patrol_msgs__msg__Task__EXPECTED_HASH, patrol_msgs__msg__Task__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = patrol_msgs__msg__Task__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint16 mission_id\n"
  "Task[] tasks";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
patrol_msgs__msg__Mission__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {patrol_msgs__msg__Mission__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 31, 31},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
patrol_msgs__msg__Mission__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *patrol_msgs__msg__Mission__get_individual_type_description_source(NULL),
    sources[1] = *patrol_msgs__msg__Task__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
