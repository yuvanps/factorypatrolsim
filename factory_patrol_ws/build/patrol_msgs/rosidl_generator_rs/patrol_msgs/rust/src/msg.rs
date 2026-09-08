#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to patrol_msgs__msg__Task

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Task::default())
  }
}

impl rosidl_runtime_rs::Message for Task {
  type RmwMsg = super::msg::rmw::Task;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        task_id: msg.task_id,
        x: msg.x,
        y: msg.y,
        z: msg.z,
        priority: msg.priority,
        inspection_type: msg.inspection_type,
        hover_duration: msg.hover_duration,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      task_id: msg.task_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      priority: msg.priority,
      inspection_type: msg.inspection_type,
      hover_duration: msg.hover_duration,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      task_id: msg.task_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      priority: msg.priority,
      inspection_type: msg.inspection_type,
      hover_duration: msg.hover_duration,
    }
  }
}


// Corresponds to patrol_msgs__msg__Mission

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Mission {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mission_id: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub tasks: Vec<super::msg::Task>,

}



impl Default for Mission {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Mission::default())
  }
}

impl rosidl_runtime_rs::Message for Mission {
  type RmwMsg = super::msg::rmw::Mission;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        mission_id: msg.mission_id,
        tasks: msg.tasks
          .into_iter()
          .map(|elem| super::msg::Task::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      mission_id: msg.mission_id,
        tasks: msg.tasks
          .iter()
          .map(|elem| super::msg::Task::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      mission_id: msg.mission_id,
      tasks: msg.tasks
          .into_iter()
          .map(super::msg::Task::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to patrol_msgs__msg__DroneState

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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

}



impl Default for DroneState {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::DroneState::default())
  }
}

impl rosidl_runtime_rs::Message for DroneState {
  type RmwMsg = super::msg::rmw::DroneState;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        drone_id: msg.drone_id,
        x: msg.x,
        y: msg.y,
        z: msg.z,
        battery_level: msg.battery_level,
        state: msg.state,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      drone_id: msg.drone_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      battery_level: msg.battery_level,
      state: msg.state,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      drone_id: msg.drone_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      battery_level: msg.battery_level,
      state: msg.state,
    }
  }
}


// Corresponds to patrol_msgs__msg__TaskBid

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TaskBid::default())
  }
}

impl rosidl_runtime_rs::Message for TaskBid {
  type RmwMsg = super::msg::rmw::TaskBid;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        drone_id: msg.drone_id,
        task_id: msg.task_id,
        cost: msg.cost,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      drone_id: msg.drone_id,
      task_id: msg.task_id,
      cost: msg.cost,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      drone_id: msg.drone_id,
      task_id: msg.task_id,
      cost: msg.cost,
    }
  }
}


// Corresponds to patrol_msgs__msg__TaskAssignment

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TaskAssignment::default())
  }
}

impl rosidl_runtime_rs::Message for TaskAssignment {
  type RmwMsg = super::msg::rmw::TaskAssignment;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        task_id: msg.task_id,
        drone_id: msg.drone_id,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      task_id: msg.task_id,
      drone_id: msg.drone_id,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      task_id: msg.task_id,
      drone_id: msg.drone_id,
    }
  }
}


// Corresponds to patrol_msgs__msg__SwarmStatus

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SwarmStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub reason: std::string::String,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::SwarmStatus::default())
  }
}

impl rosidl_runtime_rs::Message for SwarmStatus {
  type RmwMsg = super::msg::rmw::SwarmStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
        reason: msg.reason.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
        reason: msg.reason.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
      reason: msg.reason.to_string(),
    }
  }
}


