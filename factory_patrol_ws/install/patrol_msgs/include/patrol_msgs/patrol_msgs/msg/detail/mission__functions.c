// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from patrol_msgs:msg/Mission.idl
// generated code does not contain a copyright notice
#include "patrol_msgs/msg/detail/mission__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `tasks`
#include "patrol_msgs/msg/detail/task__functions.h"

bool
patrol_msgs__msg__Mission__init(patrol_msgs__msg__Mission * msg)
{
  if (!msg) {
    return false;
  }
  // mission_id
  // tasks
  if (!patrol_msgs__msg__Task__Sequence__init(&msg->tasks, 0)) {
    patrol_msgs__msg__Mission__fini(msg);
    return false;
  }
  return true;
}

void
patrol_msgs__msg__Mission__fini(patrol_msgs__msg__Mission * msg)
{
  if (!msg) {
    return;
  }
  // mission_id
  // tasks
  patrol_msgs__msg__Task__Sequence__fini(&msg->tasks);
}

bool
patrol_msgs__msg__Mission__are_equal(const patrol_msgs__msg__Mission * lhs, const patrol_msgs__msg__Mission * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // mission_id
  if (lhs->mission_id != rhs->mission_id) {
    return false;
  }
  // tasks
  if (!patrol_msgs__msg__Task__Sequence__are_equal(
      &(lhs->tasks), &(rhs->tasks)))
  {
    return false;
  }
  return true;
}

bool
patrol_msgs__msg__Mission__copy(
  const patrol_msgs__msg__Mission * input,
  patrol_msgs__msg__Mission * output)
{
  if (!input || !output) {
    return false;
  }
  // mission_id
  output->mission_id = input->mission_id;
  // tasks
  if (!patrol_msgs__msg__Task__Sequence__copy(
      &(input->tasks), &(output->tasks)))
  {
    return false;
  }
  return true;
}

patrol_msgs__msg__Mission *
patrol_msgs__msg__Mission__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__Mission * msg = (patrol_msgs__msg__Mission *)allocator.allocate(sizeof(patrol_msgs__msg__Mission), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(patrol_msgs__msg__Mission));
  bool success = patrol_msgs__msg__Mission__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
patrol_msgs__msg__Mission__destroy(patrol_msgs__msg__Mission * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    patrol_msgs__msg__Mission__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
patrol_msgs__msg__Mission__Sequence__init(patrol_msgs__msg__Mission__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__Mission * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(patrol_msgs__msg__Mission)) {
      return false;
    }
    data = (patrol_msgs__msg__Mission *)allocator.zero_allocate(size, sizeof(patrol_msgs__msg__Mission), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = patrol_msgs__msg__Mission__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        patrol_msgs__msg__Mission__fini(&data[i - 1]);
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
patrol_msgs__msg__Mission__Sequence__fini(patrol_msgs__msg__Mission__Sequence * array)
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
      patrol_msgs__msg__Mission__fini(&array->data[i]);
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

patrol_msgs__msg__Mission__Sequence *
patrol_msgs__msg__Mission__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__Mission__Sequence * array = (patrol_msgs__msg__Mission__Sequence *)allocator.allocate(sizeof(patrol_msgs__msg__Mission__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = patrol_msgs__msg__Mission__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
patrol_msgs__msg__Mission__Sequence__destroy(patrol_msgs__msg__Mission__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    patrol_msgs__msg__Mission__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
patrol_msgs__msg__Mission__Sequence__are_equal(const patrol_msgs__msg__Mission__Sequence * lhs, const patrol_msgs__msg__Mission__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!patrol_msgs__msg__Mission__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
patrol_msgs__msg__Mission__Sequence__copy(
  const patrol_msgs__msg__Mission__Sequence * input,
  patrol_msgs__msg__Mission__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(patrol_msgs__msg__Mission)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(patrol_msgs__msg__Mission);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    patrol_msgs__msg__Mission * data =
      (patrol_msgs__msg__Mission *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!patrol_msgs__msg__Mission__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          patrol_msgs__msg__Mission__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!patrol_msgs__msg__Mission__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
