// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from patrol_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice
#include "patrol_msgs/msg/detail/task_bid__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
patrol_msgs__msg__TaskBid__init(patrol_msgs__msg__TaskBid * msg)
{
  if (!msg) {
    return false;
  }
  // drone_id
  // task_id
  // cost
  return true;
}

void
patrol_msgs__msg__TaskBid__fini(patrol_msgs__msg__TaskBid * msg)
{
  if (!msg) {
    return;
  }
  // drone_id
  // task_id
  // cost
}

bool
patrol_msgs__msg__TaskBid__are_equal(const patrol_msgs__msg__TaskBid * lhs, const patrol_msgs__msg__TaskBid * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // drone_id
  if (lhs->drone_id != rhs->drone_id) {
    return false;
  }
  // task_id
  if (lhs->task_id != rhs->task_id) {
    return false;
  }
  // cost
  if (lhs->cost != rhs->cost) {
    return false;
  }
  return true;
}

bool
patrol_msgs__msg__TaskBid__copy(
  const patrol_msgs__msg__TaskBid * input,
  patrol_msgs__msg__TaskBid * output)
{
  if (!input || !output) {
    return false;
  }
  // drone_id
  output->drone_id = input->drone_id;
  // task_id
  output->task_id = input->task_id;
  // cost
  output->cost = input->cost;
  return true;
}

patrol_msgs__msg__TaskBid *
patrol_msgs__msg__TaskBid__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__TaskBid * msg = (patrol_msgs__msg__TaskBid *)allocator.allocate(sizeof(patrol_msgs__msg__TaskBid), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(patrol_msgs__msg__TaskBid));
  bool success = patrol_msgs__msg__TaskBid__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
patrol_msgs__msg__TaskBid__destroy(patrol_msgs__msg__TaskBid * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    patrol_msgs__msg__TaskBid__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
patrol_msgs__msg__TaskBid__Sequence__init(patrol_msgs__msg__TaskBid__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__TaskBid * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(patrol_msgs__msg__TaskBid)) {
      return false;
    }
    data = (patrol_msgs__msg__TaskBid *)allocator.zero_allocate(size, sizeof(patrol_msgs__msg__TaskBid), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = patrol_msgs__msg__TaskBid__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        patrol_msgs__msg__TaskBid__fini(&data[i - 1]);
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
patrol_msgs__msg__TaskBid__Sequence__fini(patrol_msgs__msg__TaskBid__Sequence * array)
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
      patrol_msgs__msg__TaskBid__fini(&array->data[i]);
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

patrol_msgs__msg__TaskBid__Sequence *
patrol_msgs__msg__TaskBid__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__TaskBid__Sequence * array = (patrol_msgs__msg__TaskBid__Sequence *)allocator.allocate(sizeof(patrol_msgs__msg__TaskBid__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = patrol_msgs__msg__TaskBid__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
patrol_msgs__msg__TaskBid__Sequence__destroy(patrol_msgs__msg__TaskBid__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    patrol_msgs__msg__TaskBid__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
patrol_msgs__msg__TaskBid__Sequence__are_equal(const patrol_msgs__msg__TaskBid__Sequence * lhs, const patrol_msgs__msg__TaskBid__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!patrol_msgs__msg__TaskBid__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
patrol_msgs__msg__TaskBid__Sequence__copy(
  const patrol_msgs__msg__TaskBid__Sequence * input,
  patrol_msgs__msg__TaskBid__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(patrol_msgs__msg__TaskBid)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(patrol_msgs__msg__TaskBid);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    patrol_msgs__msg__TaskBid * data =
      (patrol_msgs__msg__TaskBid *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!patrol_msgs__msg__TaskBid__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          patrol_msgs__msg__TaskBid__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!patrol_msgs__msg__TaskBid__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
