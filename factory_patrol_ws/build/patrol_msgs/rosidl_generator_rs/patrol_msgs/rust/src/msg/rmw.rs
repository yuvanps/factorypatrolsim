#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__Task() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__Task__init(msg: *mut Task) -> bool;
    fn patrol_msgs__msg__Task__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Task>, size: usize) -> bool;
    fn patrol_msgs__msg__Task__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Task>);
    fn patrol_msgs__msg__Task__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Task>, out_seq: *mut rosidl_runtime_rs::Sequence<Task>) -> bool;
}

// Corresponds to patrol_msgs__msg__Task
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Task {

    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub priority: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub inspection_type: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub hover_duration: f32,

}



impl Default for Task {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__Task__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__Task__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Task {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__Task__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__Task__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__Task__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Task {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Task where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/Task";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__Task() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__Mission() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__Mission__init(msg: *mut Mission) -> bool;
    fn patrol_msgs__msg__Mission__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Mission>, size: usize) -> bool;
    fn patrol_msgs__msg__Mission__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Mission>);
    fn patrol_msgs__msg__Mission__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Mission>, out_seq: *mut rosidl_runtime_rs::Sequence<Mission>) -> bool;
}

// Corresponds to patrol_msgs__msg__Mission
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Mission {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mission_id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub tasks: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Task>,

}



impl Default for Mission {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__Mission__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__Mission__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Mission {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__Mission__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__Mission__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__Mission__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Mission {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Mission where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/Mission";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__Mission() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__DroneState() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__DroneState__init(msg: *mut DroneState) -> bool;
    fn patrol_msgs__msg__DroneState__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DroneState>, size: usize) -> bool;
    fn patrol_msgs__msg__DroneState__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DroneState>);
    fn patrol_msgs__msg__DroneState__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DroneState>, out_seq: *mut rosidl_runtime_rs::Sequence<DroneState>) -> bool;
}

// Corresponds to patrol_msgs__msg__DroneState
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DroneState {

    // This member is not documented.
    #[allow(missing_docs)]
    pub drone_id: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub battery_level: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: u8,

    /// task the drone is currently flying to / inspecting (0 = none)
    pub current_task_id: u16,

}



impl Default for DroneState {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__DroneState__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__DroneState__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DroneState {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__DroneState__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__DroneState__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__DroneState__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DroneState {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DroneState where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/DroneState";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__DroneState() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__TaskBid() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__TaskBid__init(msg: *mut TaskBid) -> bool;
    fn patrol_msgs__msg__TaskBid__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TaskBid>, size: usize) -> bool;
    fn patrol_msgs__msg__TaskBid__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TaskBid>);
    fn patrol_msgs__msg__TaskBid__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TaskBid>, out_seq: *mut rosidl_runtime_rs::Sequence<TaskBid>) -> bool;
}

// Corresponds to patrol_msgs__msg__TaskBid
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TaskBid {

    // This member is not documented.
    #[allow(missing_docs)]
    pub drone_id: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cost: f32,

}



impl Default for TaskBid {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__TaskBid__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__TaskBid__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TaskBid {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__TaskBid__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__TaskBid__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__TaskBid__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TaskBid {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TaskBid where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/TaskBid";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__TaskBid() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__TaskAssignment() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__TaskAssignment__init(msg: *mut TaskAssignment) -> bool;
    fn patrol_msgs__msg__TaskAssignment__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TaskAssignment>, size: usize) -> bool;
    fn patrol_msgs__msg__TaskAssignment__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TaskAssignment>);
    fn patrol_msgs__msg__TaskAssignment__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TaskAssignment>, out_seq: *mut rosidl_runtime_rs::Sequence<TaskAssignment>) -> bool;
}

// Corresponds to patrol_msgs__msg__TaskAssignment
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TaskAssignment {

    // This member is not documented.
    #[allow(missing_docs)]
    pub task_id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub drone_id: u8,

}



impl Default for TaskAssignment {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__TaskAssignment__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__TaskAssignment__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TaskAssignment {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__TaskAssignment__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__TaskAssignment__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__TaskAssignment__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TaskAssignment {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TaskAssignment where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/TaskAssignment";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__TaskAssignment() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__SwarmStatus() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__SwarmStatus__init(msg: *mut SwarmStatus) -> bool;
    fn patrol_msgs__msg__SwarmStatus__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SwarmStatus>, size: usize) -> bool;
    fn patrol_msgs__msg__SwarmStatus__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SwarmStatus>);
    fn patrol_msgs__msg__SwarmStatus__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SwarmStatus>, out_seq: *mut rosidl_runtime_rs::Sequence<SwarmStatus>) -> bool;
}

// Corresponds to patrol_msgs__msg__SwarmStatus
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SwarmStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reason: rosidl_runtime_rs::String,

}

impl SwarmStatus {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATUS_OK: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATUS_NO_DRONES_AVAILABLE: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATUS_ALL_DRONES_LOW_BATTERY: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATUS_PATROL_CYCLE_COMPLETE: u8 = 3;

}


impl Default for SwarmStatus {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__SwarmStatus__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__SwarmStatus__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SwarmStatus {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__SwarmStatus__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__SwarmStatus__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__SwarmStatus__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SwarmStatus {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SwarmStatus where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/SwarmStatus";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__SwarmStatus() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__ExperimentEvent() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__ExperimentEvent__init(msg: *mut ExperimentEvent) -> bool;
    fn patrol_msgs__msg__ExperimentEvent__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ExperimentEvent>, size: usize) -> bool;
    fn patrol_msgs__msg__ExperimentEvent__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ExperimentEvent>);
    fn patrol_msgs__msg__ExperimentEvent__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ExperimentEvent>, out_seq: *mut rosidl_runtime_rs::Sequence<ExperimentEvent>) -> bool;
}

// Corresponds to patrol_msgs__msg__ExperimentEvent
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ExperimentEvent {

    // This member is not documented.
    #[allow(missing_docs)]
    pub timestamp: u64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub event_type: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub data: rosidl_runtime_rs::String,

}



impl Default for ExperimentEvent {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__ExperimentEvent__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__ExperimentEvent__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ExperimentEvent {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__ExperimentEvent__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__ExperimentEvent__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__ExperimentEvent__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ExperimentEvent {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ExperimentEvent where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/ExperimentEvent";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__ExperimentEvent() }
  }
}


#[link(name = "patrol_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__MovementCommand() -> *const std::ffi::c_void;
}

#[link(name = "patrol_msgs__rosidl_generator_c")]
extern "C" {
    fn patrol_msgs__msg__MovementCommand__init(msg: *mut MovementCommand) -> bool;
    fn patrol_msgs__msg__MovementCommand__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MovementCommand>, size: usize) -> bool;
    fn patrol_msgs__msg__MovementCommand__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MovementCommand>);
    fn patrol_msgs__msg__MovementCommand__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MovementCommand>, out_seq: *mut rosidl_runtime_rs::Sequence<MovementCommand>) -> bool;
}

// Corresponds to patrol_msgs__msg__MovementCommand
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Movement command from a reactive coordination algorithm (e.g. APF) to one patrol controller.
/// All positions/velocities are in the common factory frame used by DroneState and Task:
///   x = Gazebo X (east), y = Gazebo Y (north), z = -height (negative = above ground).

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MovementCommand {

    // This member is not documented.
    #[allow(missing_docs)]
    pub drone_id: u8,

    /// goal this command steers toward; controllers ignore commands for any other task
    pub task_id: u16,

    /// position setpoint the controller should track
    pub target_x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub target_z: f32,

    /// commanded velocity that produced the target (informational / diagnostics)
    pub velocity_x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub velocity_y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub velocity_z: f32,

}



impl Default for MovementCommand {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !patrol_msgs__msg__MovementCommand__init(&mut msg as *mut _) {
        panic!("Call to patrol_msgs__msg__MovementCommand__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MovementCommand {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__MovementCommand__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__MovementCommand__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { patrol_msgs__msg__MovementCommand__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MovementCommand {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MovementCommand where Self: Sized {
  const TYPE_NAME: &'static str = "patrol_msgs/msg/MovementCommand";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__patrol_msgs__msg__MovementCommand() }
  }
}


