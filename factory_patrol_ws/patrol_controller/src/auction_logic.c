#include "auction_logic.h"
#include <math.h>
#include <stdio.h>
#include <stdbool.h>

static AuctionTask tasks[MAX_TASKS];
static uint8_t num_tasks = 0;

static DroneStateInfo drones[MAX_DRONES];
static float current_bids[MAX_TASKS][MAX_DRONES];
static bool patrol_in_progress = false;

void auction_init(void) {
    num_tasks = 0;
    for (int i = 0; i < MAX_TASKS; i++) {
        tasks[i].active = false;
        tasks[i].completed = false;
        tasks[i].assigned_drone = 255;
        for (int d = 0; d < MAX_DRONES; d++) {
            current_bids[i][d] = -1.0f;
        }
    }
    for (int d = 0; d < MAX_DRONES; d++) {
        drones[d].battery_level = 100.0f;
        drones[d].state = DRONE_STATE_IDLE;
        drones[d].is_healthy = true;   // Always start healthy — don't carry over stale state
        drones[d].last_seen_us = 0;
        drones[d].x = 0.0f;
        drones[d].y = -(d * 2.0f + 1.0f);
        drones[d].z = -3.0f;
    }
}


void auction_add_task(uint16_t id, float x, float y, float z, uint8_t priority, uint8_t type, float hover) {
    if (num_tasks < MAX_TASKS) {
        tasks[num_tasks].task_id = id;
        tasks[num_tasks].x = x;
        tasks[num_tasks].y = y;
        tasks[num_tasks].z = z;
        tasks[num_tasks].priority = priority;
        tasks[num_tasks].inspection_type = type;
        tasks[num_tasks].hover_duration = hover;
        tasks[num_tasks].active = true;
        tasks[num_tasks].completed = false;
        tasks[num_tasks].assigned_drone = 255;
        num_tasks++;
    }
}

void auction_update_drone_state(uint8_t drone_id, float x, float y, float z, float battery, uint8_t state, uint64_t timestamp_us) {
    if (drone_id >= MAX_DRONES) return;
    
    drones[drone_id].x = x;
    drones[drone_id].y = y;
    drones[drone_id].z = z;
    drones[drone_id].battery_level = battery;
    drones[drone_id].state = state;
    drones[drone_id].last_seen_us = timestamp_us;
    
    if (state == DRONE_STATE_PATROLLING || state == DRONE_STATE_INSPECTING) {
        patrol_in_progress = true;
    }

    if (battery < 20.0f) {
        if (drones[drone_id].is_healthy) {
            printf("[Swarm] Drone %d battery critical (%.1f%%). Marking as UNHEALTHY.\n", drone_id, battery);
            drones[drone_id].is_healthy = false;
            auction_handle_drone_failure(drone_id);
        }
    } else {
        drones[drone_id].is_healthy = true;
    }
}

uint8_t auction_get_assigned_task_count(uint8_t drone_id) {
    uint8_t count = 0;
    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].active && tasks[i].assigned_drone == drone_id) {
            count++;
        }
    }
    return count;
}

void auction_record_bid(uint16_t task_id, uint8_t drone_id, float cost) {
    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].task_id == task_id && drone_id < MAX_DRONES) {
            current_bids[i][drone_id] = cost;
            break;
        }
    }
}

float auction_calculate_cost(uint8_t drone_id, uint16_t task_id) {
    if (drone_id >= MAX_DRONES || !drones[drone_id].is_healthy) return -1.0f;
    
    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].task_id == task_id) {
            float dx = tasks[i].x - drones[drone_id].x;
            float dy = tasks[i].y - drones[drone_id].y;
            float dz = tasks[i].z - drones[drone_id].z;
            float distance = sqrtf(dx*dx + dy*dy + dz*dz);
            
            // Workload penalty to balance assignments across all 3 drones
            float workload_penalty = auction_get_assigned_task_count(drone_id) * 15.0f;
            
            // Battery penalty
            float battery_penalty = (100.0f - drones[drone_id].battery_level) * 0.2f;
            if (battery_penalty < 0) battery_penalty = 0;

            return distance + workload_penalty + battery_penalty;
        }
    }
    return -1.0f;
}

bool auction_run_allocation(uint16_t *out_task_id, uint8_t *out_drone_id) {
    if (num_tasks == 0) return false;

    uint8_t healthy_drones = 0;
    for (int d = 0; d < MAX_DRONES; d++) {
        if (drones[d].is_healthy) healthy_drones++;
    }
    if (healthy_drones == 0) healthy_drones = 1;

    // Cap tasks per drone so all 3 drones get an equal share of inspection points
    uint8_t max_per_drone = (num_tasks + healthy_drones - 1) / healthy_drones;

    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].active && tasks[i].assigned_drone == 255) {
            float best_cost = 999999.0f;
            uint8_t best_drone = 255;
            
            for (int d = 0; d < MAX_DRONES; d++) {
                if (drones[d].is_healthy && auction_get_assigned_task_count(d) < max_per_drone) {
                    float cost = auction_calculate_cost(d, tasks[i].task_id);
                    if (cost >= 0.0f && cost < best_cost) {
                        best_cost = cost;
                        best_drone = d;
                    }
                }
            }
            
            if (best_drone != 255) {
                tasks[i].assigned_drone = best_drone;
                *out_task_id = tasks[i].task_id;
                *out_drone_id = best_drone;
                return true;
            }
        }
    }
    return false;
}

void auction_handle_drone_failure(uint8_t failed_drone_id) {
    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].assigned_drone == failed_drone_id && tasks[i].active) {
            printf("[Swarm] Revoking Task %d from failed Drone %d and re-auctioning...\n", tasks[i].task_id, failed_drone_id);
            tasks[i].assigned_drone = 255;
            for (int d = 0; d < MAX_DRONES; d++) {
                if (d != failed_drone_id && drones[d].is_healthy) {
                    current_bids[i][d] = auction_calculate_cost(d, tasks[i].task_id);
                } else {
                    current_bids[i][d] = -1.0f;
                }
            }
        }
    }
}

void auction_check_peer_timeouts(uint64_t current_time_us, uint64_t timeout_us) {
    for (int d = 0; d < MAX_DRONES; d++) {
        if (drones[d].is_healthy && drones[d].last_seen_us > 0) {
            if (current_time_us > drones[d].last_seen_us + timeout_us) {
                drones[d].is_healthy = false;
                drones[d].state = DRONE_STATE_FAILED;
                printf("[Swarm] Heartbeat timeout for Drone %d. Marking as FAILED.\n", d);
                auction_handle_drone_failure(d);
            }
        }
    }
}

void auction_recycle_tasks_if_all_completed(void) {
    if (num_tasks == 0) return;
    
    // Count how many tasks are done vs still active/pending
    uint8_t completed_count = 0;
    uint8_t active_count = 0;
    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].completed) completed_count++;
        if (tasks[i].active) active_count++;
    }
    
    // All tasks must be completed (none still active) and a patrol must have run
    if (completed_count == num_tasks && active_count == 0 && patrol_in_progress) {
        patrol_in_progress = false; // Reset for next cycle
        printf("\n==========================================================\n");
        printf(" [Swarm] Patrol cycle complete! Resetting inspection points\n");
        printf("         for CONTINUOUS FACTORY SURVEILLANCE LOOP...      \n");
        printf("==========================================================\n\n");
        for (int i = 0; i < num_tasks; i++) {
            tasks[i].active = true;
            tasks[i].completed = false;
            tasks[i].assigned_drone = 255;
            for (int d = 0; d < MAX_DRONES; d++) {
                if (drones[d].is_healthy) {
                    current_bids[i][d] = auction_calculate_cost(d, tasks[i].task_id);
                } else {
                    current_bids[i][d] = -1.0f;
                }
            }
        }
    }
}

AuctionTask* auction_get_task(uint16_t task_id) {
    for (int i = 0; i < num_tasks; i++) {
        if (tasks[i].task_id == task_id) {
            return &tasks[i];
        }
    }
    return 0;
}

AuctionTask* auction_get_tasks(uint8_t *count) {
    *count = num_tasks;
    return tasks;
}

bool auction_is_drone_healthy(uint8_t drone_id) {
    if (drone_id < MAX_DRONES) {
        return drones[drone_id].is_healthy;
    }
    return false;
}

uint8_t auction_count_healthy_drones(void) {
    uint8_t count = 0;
    for (int d = 0; d < MAX_DRONES; d++) {
        if (drones[d].is_healthy) count++;
    }
    return count;
}

void auction_get_drone_position(uint8_t drone_id, float *x, float *y, float *z) {
    if (drone_id < MAX_DRONES) {
        *x = drones[drone_id].x;
        *y = drones[drone_id].y;
        *z = drones[drone_id].z;
    } else {
        *x = 0.0f; *y = 0.0f; *z = 0.0f;
    }
}
