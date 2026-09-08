// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from patrol_msgs:msg/Mission.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "patrol_msgs/msg/mission.hpp"


#ifndef PATROL_MSGS__MSG__DETAIL__MISSION__STRUCT_HPP_
#define PATROL_MSGS__MSG__DETAIL__MISSION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'tasks'
#include "patrol_msgs/msg/detail/task__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__patrol_msgs__msg__Mission __attribute__((deprecated))
#else
# define DEPRECATED__patrol_msgs__msg__Mission __declspec(deprecated)
#endif

namespace patrol_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Mission_
{
  using Type = Mission_<ContainerAllocator>;

  explicit Mission_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_id = 0;
    }
  }

  explicit Mission_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_id = 0;
    }
  }

  // field types and members
  using _mission_id_type =
    uint16_t;
  _mission_id_type mission_id;
  using _tasks_type =
    std::vector<patrol_msgs::msg::Task_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<patrol_msgs::msg::Task_<ContainerAllocator>>>;
  _tasks_type tasks;

  // setters for named parameter idiom
  Type & set__mission_id(
    const uint16_t & _arg)
  {
    this->mission_id = _arg;
    return *this;
  }
  Type & set__tasks(
    const std::vector<patrol_msgs::msg::Task_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<patrol_msgs::msg::Task_<ContainerAllocator>>> & _arg)
  {
    this->tasks = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    patrol_msgs::msg::Mission_<ContainerAllocator> *;
  using ConstRawPtr =
    const patrol_msgs::msg::Mission_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<patrol_msgs::msg::Mission_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<patrol_msgs::msg::Mission_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::Mission_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::Mission_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      patrol_msgs::msg::Mission_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<patrol_msgs::msg::Mission_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<patrol_msgs::msg::Mission_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<patrol_msgs::msg::Mission_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__patrol_msgs__msg__Mission
    std::shared_ptr<patrol_msgs::msg::Mission_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__patrol_msgs__msg__Mission
    std::shared_ptr<patrol_msgs::msg::Mission_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Mission_ & other) const
  {
    if (this->mission_id != other.mission_id) {
      return false;
    }
    if (this->tasks != other.tasks) {
      return false;
    }
    return true;
  }
  bool operator!=(const Mission_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Mission_

// alias to use template instance with default allocator
using Mission =
  patrol_msgs::msg::Mission_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace patrol_msgs

#endif  // PATROL_MSGS__MSG__DETAIL__MISSION__STRUCT_HPP_
