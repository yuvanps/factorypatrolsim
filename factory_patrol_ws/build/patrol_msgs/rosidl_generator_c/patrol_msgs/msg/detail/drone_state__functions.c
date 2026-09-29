// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from patrol_msgs:msg/DroneState.idl
// generated code does not contain a copyright notice
#include "patrol_msgs/msg/detail/drone_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
patrol_msgs__msg__DroneState__init(patrol_msgs__msg__DroneState * msg)
{
  if (!msg) {
    return false;
  }
  // drone_id
  // x
  // y
  // z
  // battery_level
  // state
  // current_task_id
  return true;
}

void
patrol_msgs__msg__DroneState__fini(patrol_msgs__msg__DroneState * msg)
{
  if (!msg) {
    return;
  }
  // drone_id
  // x
  // y
  // z
  // battery_level
  // state
  // current_task_id
}

bool
patrol_msgs__msg__DroneState__are_equal(const patrol_msgs__msg__DroneState * lhs, const patrol_msgs__msg__DroneState * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // drone_id
  if (lhs->drone_id != rhs->drone_id) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // z
  if (lhs->z != rhs->z) {
    return false;
  }
  // battery_level
  if (lhs->battery_level != rhs->battery_level) {
    return false;
  }
  // state
  if (lhs->state != rhs->state) {
    return false;
  }
  // current_task_id
  if (lhs->current_task_id != rhs->current_task_id) {
    return false;
  }
  return true;
}

bool
patrol_msgs__msg__DroneState__copy(
  const patrol_msgs__msg__DroneState * input,
  patrol_msgs__msg__DroneState * output)
{
  if (!input || !output) {
    return false;
  }
  // drone_id
  output->drone_id = input->drone_id;
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // z
  output->z = input->z;
  // battery_level
  output->battery_level = input->battery_level;
  // state
  output->state = input->state;
  // current_task_id
  output->current_task_id = input->current_task_id;
  return true;
}

patrol_msgs__msg__DroneState *
patrol_msgs__msg__DroneState__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__DroneState * msg = (patrol_msgs__msg__DroneState *)allocator.allocate(sizeof(patrol_msgs__msg__DroneState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(patrol_msgs__msg__DroneState));
  bool success = patrol_msgs__msg__DroneState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
patrol_msgs__msg__DroneState__destroy(patrol_msgs__msg__DroneState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    patrol_msgs__msg__DroneState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
patrol_msgs__msg__DroneState__Sequence__init(patrol_msgs__msg__DroneState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__DroneState * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(patrol_msgs__msg__DroneState)) {
      return false;
    }
    data = (patrol_msgs__msg__DroneState *)allocator.zero_allocate(size, sizeof(patrol_msgs__msg__DroneState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = patrol_msgs__msg__DroneState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        patrol_msgs__msg__DroneState__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
patrol_msgs__msg__DroneState__Sequence__fini(patrol_msgs__msg__DroneState__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      patrol_msgs__msg__DroneState__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

patrol_msgs__msg__DroneState__Sequence *
patrol_msgs__msg__DroneState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__DroneState__Sequence * array = (patrol_msgs__msg__DroneState__Sequence *)allocator.allocate(sizeof(patrol_msgs__msg__DroneState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = patrol_msgs__msg__DroneState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
patrol_msgs__msg__DroneState__Sequence__destroy(patrol_msgs__msg__DroneState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    patrol_msgs__msg__DroneState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
patrol_msgs__msg__DroneState__Sequence__are_equal(const patrol_msgs__msg__DroneState__Sequence * lhs, const patrol_msgs__msg__DroneState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!patrol_msgs__msg__DroneState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
patrol_msgs__msg__DroneState__Sequence__copy(
  const patrol_msgs__msg__DroneState__Sequence * input,
  patrol_msgs__msg__DroneState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(patrol_msgs__msg__DroneState)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(patrol_msgs__msg__DroneState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    patrol_msgs__msg__DroneState * data =
      (patrol_msgs__msg__DroneState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!patrol_msgs__msg__DroneState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          patrol_msgs__msg__DroneState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!patrol_msgs__msg__DroneState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
