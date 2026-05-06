# Simulation Metrics Format

## Session 7 and Earlier (Single-UAV)
```csv
metric,value
detected,false
detection_time_seconds,-1
uav_path_length_meters,664.69
cooperation_gain,0
```

## Phase 0 and Later (Multi-UAV Ready)
```csv
metric,value
detected,false
detection_time_seconds,-1
uav_count,1
uav_0_path_length_meters,664.69
total_uav_path_length_meters,664.69
cooperation_overlap_ratio,0.0
cooperation_gain,0
```

### Migration Notes
- Old scripts reading `uav_path_length_meters` will fail
- Use `total_uav_path_length_meters` instead
- For single UAV: `total` = `uav_0` value
