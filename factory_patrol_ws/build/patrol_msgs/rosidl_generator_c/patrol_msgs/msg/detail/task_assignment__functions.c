// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from patrol_msgs:msg/TaskAssignment.idl
// generated code does not contain a copyright notice
#include "patrol_msgs/msg/detail/task_assignment__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
patrol_msgs__msg__TaskAssignment__init(patrol_msgs__msg__TaskAssignment * msg)
{
  if (!msg) {
    return false;
  }
  // task_id
  // drone_id
  return true;
}

void
patrol_msgs__msg__TaskAssignment__fini(patrol_msgs__msg__TaskAssignment * msg)
{
  if (!msg) {
    return;
  }
  // task_id
  // drone_id
}

bool
patrol_msgs__msg__TaskAssignment__are_equal(const patrol_msgs__msg__TaskAssignment * lhs, const patrol_msgs__msg__TaskAssignment * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // task_id
  if (lhs->task_id != rhs->task_id) {
    return false;
  }
  // drone_id
  if (lhs->drone_id != rhs->drone_id) {
    return false;
  }
  return true;
}

bool
patrol_msgs__msg__TaskAssignment__copy(
  const patrol_msgs__msg__TaskAssignment * input,
  patrol_msgs__msg__TaskAssignment * output)
{
  if (!input || !output) {
    return false;
  }
  // task_id
  output->task_id = input->task_id;
  // drone_id
  output->drone_id = input->drone_id;
  return true;
}

patrol_msgs__msg__TaskAssignment *
patrol_msgs__msg__TaskAssignment__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__TaskAssignment * msg = (patrol_msgs__msg__TaskAssignment *)allocator.allocate(sizeof(patrol_msgs__msg__TaskAssignment), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(patrol_msgs__msg__TaskAssignment));
  bool success = patrol_msgs__msg__TaskAssignment__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
patrol_msgs__msg__TaskAssignment__destroy(patrol_msgs__msg__TaskAssignment * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    patrol_msgs__msg__TaskAssignment__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
patrol_msgs__msg__TaskAssignment__Sequence__init(patrol_msgs__msg__TaskAssignment__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__TaskAssignment * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(patrol_msgs__msg__TaskAssignment)) {
      return false;
    }
    data = (patrol_msgs__msg__TaskAssignment *)allocator.zero_allocate(size, sizeof(patrol_msgs__msg__TaskAssignment), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = patrol_msgs__msg__TaskAssignment__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        patrol_msgs__msg__TaskAssignment__fini(&data[i - 1]);
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
patrol_msgs__msg__TaskAssignment__Sequence__fini(patrol_msgs__msg__TaskAssignment__Sequence * array)
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
      patrol_msgs__msg__TaskAssignment__fini(&array->data[i]);
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

patrol_msgs__msg__TaskAssignment__Sequence *
patrol_msgs__msg__TaskAssignment__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__TaskAssignment__Sequence * array = (patrol_msgs__msg__TaskAssignment__Sequence *)allocator.allocate(sizeof(patrol_msgs__msg__TaskAssignment__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = patrol_msgs__msg__TaskAssignment__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
patrol_msgs__msg__TaskAssignment__Sequence__destroy(patrol_msgs__msg__TaskAssignment__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    patrol_msgs__msg__TaskAssignment__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
patrol_msgs__msg__TaskAssignment__Sequence__are_equal(const patrol_msgs__msg__TaskAssignment__Sequence * lhs, const patrol_msgs__msg__TaskAssignment__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!patrol_msgs__msg__TaskAssignment__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
patrol_msgs__msg__TaskAssignment__Sequence__copy(
  const patrol_msgs__msg__TaskAssignment__Sequence * input,
  patrol_msgs__msg__TaskAssignment__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(patrol_msgs__msg__TaskAssignment)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(patrol_msgs__msg__TaskAssignment);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    patrol_msgs__msg__TaskAssignment * data =
      (patrol_msgs__msg__TaskAssignment *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!patrol_msgs__msg__TaskAssignment__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          patrol_msgs__msg__TaskAssignment__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!patrol_msgs__msg__TaskAssignment__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
