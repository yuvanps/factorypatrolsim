// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from patrol_msgs:msg/ExperimentEvent.idl
// generated code does not contain a copyright notice
#include "patrol_msgs/msg/detail/experiment_event__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `event_type`
// Member `data`
#include "rosidl_runtime_c/string_functions.h"

bool
patrol_msgs__msg__ExperimentEvent__init(patrol_msgs__msg__ExperimentEvent * msg)
{
  if (!msg) {
    return false;
  }
  // timestamp
  // event_type
  if (!rosidl_runtime_c__String__init(&msg->event_type)) {
    patrol_msgs__msg__ExperimentEvent__fini(msg);
    return false;
  }
  // data
  if (!rosidl_runtime_c__String__init(&msg->data)) {
    patrol_msgs__msg__ExperimentEvent__fini(msg);
    return false;
  }
  return true;
}

void
patrol_msgs__msg__ExperimentEvent__fini(patrol_msgs__msg__ExperimentEvent * msg)
{
  if (!msg) {
    return;
  }
  // timestamp
  // event_type
  rosidl_runtime_c__String__fini(&msg->event_type);
  // data
  rosidl_runtime_c__String__fini(&msg->data);
}

bool
patrol_msgs__msg__ExperimentEvent__are_equal(const patrol_msgs__msg__ExperimentEvent * lhs, const patrol_msgs__msg__ExperimentEvent * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // timestamp
  if (lhs->timestamp != rhs->timestamp) {
    return false;
  }
  // event_type
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->event_type), &(rhs->event_type)))
  {
    return false;
  }
  // data
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->data), &(rhs->data)))
  {
    return false;
  }
  return true;
}

bool
patrol_msgs__msg__ExperimentEvent__copy(
  const patrol_msgs__msg__ExperimentEvent * input,
  patrol_msgs__msg__ExperimentEvent * output)
{
  if (!input || !output) {
    return false;
  }
  // timestamp
  output->timestamp = input->timestamp;
  // event_type
  if (!rosidl_runtime_c__String__copy(
      &(input->event_type), &(output->event_type)))
  {
    return false;
  }
  // data
  if (!rosidl_runtime_c__String__copy(
      &(input->data), &(output->data)))
  {
    return false;
  }
  return true;
}

patrol_msgs__msg__ExperimentEvent *
patrol_msgs__msg__ExperimentEvent__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__ExperimentEvent * msg = (patrol_msgs__msg__ExperimentEvent *)allocator.allocate(sizeof(patrol_msgs__msg__ExperimentEvent), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(patrol_msgs__msg__ExperimentEvent));
  bool success = patrol_msgs__msg__ExperimentEvent__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
patrol_msgs__msg__ExperimentEvent__destroy(patrol_msgs__msg__ExperimentEvent * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    patrol_msgs__msg__ExperimentEvent__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
patrol_msgs__msg__ExperimentEvent__Sequence__init(patrol_msgs__msg__ExperimentEvent__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__ExperimentEvent * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(patrol_msgs__msg__ExperimentEvent)) {
      return false;
    }
    data = (patrol_msgs__msg__ExperimentEvent *)allocator.zero_allocate(size, sizeof(patrol_msgs__msg__ExperimentEvent), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = patrol_msgs__msg__ExperimentEvent__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        patrol_msgs__msg__ExperimentEvent__fini(&data[i - 1]);
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
patrol_msgs__msg__ExperimentEvent__Sequence__fini(patrol_msgs__msg__ExperimentEvent__Sequence * array)
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
      patrol_msgs__msg__ExperimentEvent__fini(&array->data[i]);
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

patrol_msgs__msg__ExperimentEvent__Sequence *
patrol_msgs__msg__ExperimentEvent__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  patrol_msgs__msg__ExperimentEvent__Sequence * array = (patrol_msgs__msg__ExperimentEvent__Sequence *)allocator.allocate(sizeof(patrol_msgs__msg__ExperimentEvent__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = patrol_msgs__msg__ExperimentEvent__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
patrol_msgs__msg__ExperimentEvent__Sequence__destroy(patrol_msgs__msg__ExperimentEvent__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    patrol_msgs__msg__ExperimentEvent__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
patrol_msgs__msg__ExperimentEvent__Sequence__are_equal(const patrol_msgs__msg__ExperimentEvent__Sequence * lhs, const patrol_msgs__msg__ExperimentEvent__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!patrol_msgs__msg__ExperimentEvent__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
patrol_msgs__msg__ExperimentEvent__Sequence__copy(
  const patrol_msgs__msg__ExperimentEvent__Sequence * input,
  patrol_msgs__msg__ExperimentEvent__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(patrol_msgs__msg__ExperimentEvent)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(patrol_msgs__msg__ExperimentEvent);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    patrol_msgs__msg__ExperimentEvent * data =
      (patrol_msgs__msg__ExperimentEvent *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!patrol_msgs__msg__ExperimentEvent__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          patrol_msgs__msg__ExperimentEvent__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!patrol_msgs__msg__ExperimentEvent__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
