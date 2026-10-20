# from uav-l2/; meander_compare with an extra colour and marker for the second set (not in the committed script)
python3 -c "
import sys; sys.path.insert(0,'tools')
import meander_compare as mc
mc.COL['meanderParallel'] = '#eda100'; mc.MARK['meanderParallel'] = 'D'
sys.argv = ['x', '--set', 'meander', '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MM/k*', '--set', 'meanderParallel', '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k*', '--draws', '100', '--out', '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/mmtest/abl', '--figs', '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/mmtest']
mc.main()"
