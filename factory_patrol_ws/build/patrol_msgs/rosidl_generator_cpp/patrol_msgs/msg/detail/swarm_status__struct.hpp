// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from patrol_msgs:msg/SwarmStatus.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/swarm_status.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__STRUCT_HPP_
#define PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__patrol_msgs__msg__SwarmStatus __attribute__((deprecated))
#else
# define DEPRECATED__patrol_msgs__msg__SwarmStatus __declspec(deprecated)
#endif

namespace patrol_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SwarmStatus_
{
  using Type = SwarmStatus_<ContainerAllocator>;

  explicit SwarmStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
      this->reason = "";
    }
  }

  explicit SwarmStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : reason(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
      this->reason = "";
    }
  }

  // field types and members
  using _status_type =
    uint8_t;
  _status_type status;
  using _reason_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _reason_type reason;

  // setters for named parameter idiom
  Type & set__status(
    const uint8_t & _arg)
  {
    this->status = _arg;
    return *this;
  }
  Type & set__reason(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->reason = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t STATUS_OK =
    0u;
  static constexpr uint8_t STATUS_NO_DRONES_AVAILABLE =
    1u;
  static constexpr uint8_t STATUS_ALL_DRONES_LOW_BATTERY =
    2u;
  static constexpr uint8_t STATUS_PATROL_CYCLE_COMPLETE =
    3u;

  // pointer types
  using RawPtr =
    patrol_msgs::msg::SwarmStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const patrol_msgs::msg::SwarmStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::SwarmStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::SwarmStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__patrol_msgs__msg__SwarmStatus
    std::shared_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__patrol_msgs__msg__SwarmStatus
    std::shared_ptr<patrol_msgs::msg::SwarmStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SwarmStatus_ & other) const
  {
    if (this->status != other.status) {
      return false;
    }
    if (this->reason != other.reason) {
      return false;
    }
    return true;
  }
  bool operator!=(const SwarmStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SwarmStatus_

// alias to use template instance with default allocator
using SwarmStatus =
  patrol_msgs::msg::SwarmStatus_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SwarmStatus_<ContainerAllocator>::STATUS_OK;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SwarmStatus_<ContainerAllocator>::STATUS_NO_DRONES_AVAILABLE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SwarmStatus_<ContainerAllocator>::STATUS_ALL_DRONES_LOW_BATTERY;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SwarmStatus_<ContainerAllocator>::STATUS_PATROL_CYCLE_COMPLETE;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__SWARM_STATUS__STRUCT_HPP_
