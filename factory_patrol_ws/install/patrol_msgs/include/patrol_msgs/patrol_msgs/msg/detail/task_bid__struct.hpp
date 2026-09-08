// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from patrol_msgs:msg/TaskBid.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/task_bid.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__TASK_BID__STRUCT_HPP_
#define PATROL_MSGS__MSG__DETAIL__TASK_BID__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__patrol_msgs__msg__TaskBid __attribute__((deprecated))
#else
# define DEPRECATED__patrol_msgs__msg__TaskBid __declspec(deprecated)
#endif

namespace patrol_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TaskBid_
{
  using Type = TaskBid_<ContainerAllocator>;

  explicit TaskBid_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0;
      this->task_id = 0;
      this->cost = 0.0f;
    }
  }

  explicit TaskBid_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0;
      this->task_id = 0;
      this->cost = 0.0f;
    }
  }

  // field types and members
  using _drone_id_type =
    uint8_t;
  _drone_id_type drone_id;
  using _task_id_type =
    uint16_t;
  _task_id_type task_id;
  using _cost_type =
    float;
  _cost_type cost;

  // setters for named parameter idiom
  Type & set__drone_id(
    const uint8_t & _arg)
  {
    this->drone_id = _arg;
    return *this;
  }
  Type & set__task_id(
    const uint16_t & _arg)
  {
    this->task_id = _arg;
    return *this;
  }
  Type & set__cost(
    const float & _arg)
  {
    this->cost = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    patrol_msgs::msg::TaskBid_<ContainerAllocator> *;
  using ConstRawPtr =
    const patrol_msgs::msg::TaskBid_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::TaskBid_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::TaskBid_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__patrol_msgs__msg__TaskBid
    std::shared_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__patrol_msgs__msg__TaskBid
    std::shared_ptr<patrol_msgs::msg::TaskBid_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TaskBid_ & other) const
  {
    if (this->drone_id != other.drone_id) {
      return false;
    }
    if (this->task_id != other.task_id) {
      return false;
    }
    if (this->cost != other.cost) {
      return false;
    }
    return true;
  }
  bool operator!=(const TaskBid_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TaskBid_

// alias to use template instance with default allocator
using TaskBid =
  patrol_msgs::msg::TaskBid_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__TASK_BID__STRUCT_HPP_
