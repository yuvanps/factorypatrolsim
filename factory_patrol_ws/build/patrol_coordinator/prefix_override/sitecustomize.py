import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/mrweirdo/factory_patrol_sim/factory_patrol_ws/install/patrol_coordinator'
