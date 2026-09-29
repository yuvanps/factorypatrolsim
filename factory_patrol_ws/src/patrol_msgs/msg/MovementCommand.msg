# Movement command from a reactive coordination algorithm (e.g. APF) to one patrol controller.
# All positions/velocities are in the common factory frame used by DroneState and Task:
#   x = Gazebo X (east), y = Gazebo Y (north), z = -height (negative = above ground).
uint8 drone_id
uint16 task_id      # goal this command steers toward; controllers ignore commands for any other task
float32 target_x    # position setpoint the controller should track
float32 target_y
float32 target_z
float32 velocity_x  # commanded velocity that produced the target (informational / diagnostics)
float32 velocity_y
float32 velocity_z
