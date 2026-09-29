// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from patrol_msgs:msg/ExperimentEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/experiment_event.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__STRUCT_HPP_
#define PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__patrol_msgs__msg__ExperimentEvent __attribute__((deprecated))
#else
# define DEPRECATED__patrol_msgs__msg__ExperimentEvent __declspec(deprecated)
#endif

namespace patrol_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ExperimentEvent_
{
  using Type = ExperimentEvent_<ContainerAllocator>;

  explicit ExperimentEvent_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->timestamp = 0ull;
      this->event_type = "";
      this->data = "";
    }
  }

  explicit ExperimentEvent_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : event_type(_alloc),
    data(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->timestamp = 0ull;
      this->event_type = "";
      this->data = "";
    }
  }

  // field types and members
  using _timestamp_type =
    uint64_t;
  _timestamp_type timestamp;
  using _event_type_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _event_type_type event_type;
  using _data_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _data_type data;

  // setters for named parameter idiom
  Type & set__timestamp(
    const uint64_t & _arg)
  {
    this->timestamp = _arg;
    return *this;
  }
  Type & set__event_type(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->event_type = _arg;
    return *this;
  }
  Type & set__data(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->data = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    patrol_msgs::msg::ExperimentEvent_<ContainerAllocator> *;
  using ConstRawPtr =
    const patrol_msgs::msg::ExperimentEvent_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::ExperimentEvent_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::ExperimentEvent_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__patrol_msgs__msg__ExperimentEvent
    std::shared_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__patrol_msgs__msg__ExperimentEvent
    std::shared_ptr<patrol_msgs::msg::ExperimentEvent_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExperimentEvent_ & other) const
  {
    if (this->timestamp != other.timestamp) {
      return false;
    }
    if (this->event_type != other.event_type) {
      return false;
    }
    if (this->data != other.data) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExperimentEvent_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExperimentEvent_

// alias to use template instance with default allocator
using ExperimentEvent =
  patrol_msgs::msg::ExperimentEvent_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__EXPERIMENT_EVENT__STRUCT_HPP_
