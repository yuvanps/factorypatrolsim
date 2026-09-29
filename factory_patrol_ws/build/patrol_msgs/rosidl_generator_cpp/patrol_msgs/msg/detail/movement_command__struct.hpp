// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from patrol_msgs:msg/MovementCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/movement_command.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__STRUCT_HPP_
#define PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__patrol_msgs__msg__MovementCommand __attribute__((deprecated))
#else
# define DEPRECATED__patrol_msgs__msg__MovementCommand __declspec(deprecated)
#endif

namespace patrol_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MovementCommand_
{
  using Type = MovementCommand_<ContainerAllocator>;

  explicit MovementCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0;
      this->task_id = 0;
      this->target_x = 0.0f;
      this->target_y = 0.0f;
      this->target_z = 0.0f;
      this->velocity_x = 0.0f;
      this->velocity_y = 0.0f;
      this->velocity_z = 0.0f;
    }
  }

  explicit MovementCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0;
      this->task_id = 0;
      this->target_x = 0.0f;
      this->target_y = 0.0f;
      this->target_z = 0.0f;
      this->velocity_x = 0.0f;
      this->velocity_y = 0.0f;
      this->velocity_z = 0.0f;
    }
  }

  // field types and members
  using _drone_id_type =
    uint8_t;
  _drone_id_type drone_id;
  using _task_id_type =
    uint16_t;
  _task_id_type task_id;
  using _target_x_type =
    float;
  _target_x_type target_x;
  using _target_y_type =
    float;
  _target_y_type target_y;
  using _target_z_type =
    float;
  _target_z_type target_z;
  using _velocity_x_type =
    float;
  _velocity_x_type velocity_x;
  using _velocity_y_type =
    float;
  _velocity_y_type velocity_y;
  using _velocity_z_type =
    float;
  _velocity_z_type velocity_z;

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
  Type & set__target_x(
    const float & _arg)
  {
    this->target_x = _arg;
    return *this;
  }
  Type & set__target_y(
    const float & _arg)
  {
    this->target_y = _arg;
    return *this;
  }
  Type & set__target_z(
    const float & _arg)
  {
    this->target_z = _arg;
    return *this;
  }
  Type & set__velocity_x(
    const float & _arg)
  {
    this->velocity_x = _arg;
    return *this;
  }
  Type & set__velocity_y(
    const float & _arg)
  {
    this->velocity_y = _arg;
    return *this;
  }
  Type & set__velocity_z(
    const float & _arg)
  {
    this->velocity_z = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    patrol_msgs::msg::MovementCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const patrol_msgs::msg::MovementCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::MovementCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::MovementCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__patrol_msgs__msg__MovementCommand
    std::shared_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__patrol_msgs__msg__MovementCommand
    std::shared_ptr<patrol_msgs::msg::MovementCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MovementCommand_ & other) const
  {
    if (this->drone_id != other.drone_id) {
      return false;
    }
    if (this->task_id != other.task_id) {
      return false;
    }
    if (this->target_x != other.target_x) {
      return false;
    }
    if (this->target_y != other.target_y) {
      return false;
    }
    if (this->target_z != other.target_z) {
      return false;
    }
    if (this->velocity_x != other.velocity_x) {
      return false;
    }
    if (this->velocity_y != other.velocity_y) {
      return false;
    }
    if (this->velocity_z != other.velocity_z) {
      return false;
    }
    return true;
  }
  bool operator!=(const MovementCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MovementCommand_

// alias to use template instance with default allocator
using MovementCommand =
  patrol_msgs::msg::MovementCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__MOVEMENT_COMMAND__STRUCT_HPP_
