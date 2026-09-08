// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice
#include "patrol_msgs/msg/detail/swarm_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `reason`
#include "rosidl_runtime_c/string_functions.h"

bool
patrol_msgs__msg__SwarmStatus__init(patrol_msgs__msg__SwarmStatus * msg)
{
  if (!msg) {
    return false;
  }
  // status
  // reason
  if (!rosidl_runtime_c__String__init(&msg->reason)) {
    patrol_msgs__msg__SwarmStatus__fini(msg);
    return false;
  }
  return true;
}

void
patrol_msgs__msg__SwarmStatus__fini(patrol_msgs__msg__SwarmStatus * msg)
{
  if (!msg) {
    return;
  }
  // status
  // reason
  rosidl_runtime_c__String__fini(&msg->reason);
}

bool
patrol_msgs__msg__SwarmStatus__are_equal(const patrol_msgs__msg__SwarmStatus * lhs, const patrol_msgs__msg__SwarmStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // status
  if (lhs->status != rhs->status) {
    return false;
  }
  // reason
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->reason), &(rhs->reason)))
  {
    return false;
  }
  return true;
}

bool
patrol_msgs__msg__SwarmStatus__copy(
  const patrol_msgs__msg__SwarmStatus * input,
  patrol_msgs__msg__SwarmStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // status
  output->status = input->status;
  // reason
  if (!rosidl_runtime_c__String__copy(
      &(input->reason), &(output->reason)))
  {
    return false;
  }
  return true;
}

patrol_msgs__msg__SwarmStatus *
patrol_msgs__msg__SwarmStatus__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__SwarmStatus * msg = (patrol_msgs__msg__SwarmStatus *)allocator.allocate(sizeof(patrol_msgs__msg__SwarmStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(patrol_msgs__msg__SwarmStatus));
  bool success = patrol_msgs__msg__SwarmStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
patrol_msgs__msg__SwarmStatus__destroy(patrol_msgs__msg__SwarmStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    patrol_msgs__msg__SwarmStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
patrol_msgs__msg__SwarmStatus__Sequence__init(patrol_msgs__msg__SwarmStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__SwarmStatus * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(patrol_msgs__msg__SwarmStatus)) {
      return false;
    }
    data = (patrol_msgs__msg__SwarmStatus *)allocator.zero_allocate(size, sizeof(patrol_msgs__msg__SwarmStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = patrol_msgs__msg__SwarmStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        patrol_msgs__msg__SwarmStatus__fini(&data[i - 1]);
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
patrol_msgs__msg__SwarmStatus__Sequence__fini(patrol_msgs__msg__SwarmStatus__Sequence * array)
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
      patrol_msgs__msg__SwarmStatus__fini(&array->data[i]);
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

patrol_msgs__msg__SwarmStatus__Sequence *
patrol_msgs__msg__SwarmStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__SwarmStatus__Sequence * array = (patrol_msgs__msg__SwarmStatus__Sequence *)allocator.allocate(sizeof(patrol_msgs__msg__SwarmStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = patrol_msgs__msg__SwarmStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
patrol_msgs__msg__SwarmStatus__Sequence__destroy(patrol_msgs__msg__SwarmStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    patrol_msgs__msg__SwarmStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
patrol_msgs__msg__SwarmStatus__Sequence__are_equal(const patrol_msgs__msg__SwarmStatus__Sequence * lhs, const patrol_msgs__msg__SwarmStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!patrol_msgs__msg__SwarmStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
patrol_msgs__msg__SwarmStatus__Sequence__copy(
  const patrol_msgs__msg__SwarmStatus__Sequence * input,
  patrol_msgs__msg__SwarmStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(patrol_msgs__msg__SwarmStatus)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(patrol_msgs__msg__SwarmStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    patrol_msgs__msg__SwarmStatus * data =
      (patrol_msgs__msg__SwarmStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!patrol_msgs__msg__SwarmStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          patrol_msgs__msg__SwarmStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!patrol_msgs__msg__SwarmStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
