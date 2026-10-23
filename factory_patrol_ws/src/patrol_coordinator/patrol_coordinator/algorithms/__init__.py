"""Coordination algorithm implementations.

Available algorithms:
    - auction: Market-based auction (runs natively in C controller)
    - pso: Particle Swarm Optimization (not yet implemented)
    - apf: Artificial Potential Field reactive movement (goal attraction +
           obstacle and drone repulsion)
    - rl:  trained PPO leg planner (rl-nmopso-factory-patrol) + path following;
           needs the RL virtual environment (torch), see config/algorithms/rl.yaml
    - nmopso: NMOPSO leg planner (vectorised port of the authors' NMOPSO.m) with the RL algorithm's
           path following; plans cached by scripts/precompute_nmopso_cache.py, see config/algorithms/nmopso.yaml
"""

ALGORITHM_REGISTRY = {
    'auction': 'patrol_coordinator.algorithms.auction.AuctionAlgorithm',
    'pso': 'patrol_coordinator.algorithms.pso_stub.PSOAlgorithm',
    'apf': 'patrol_coordinator.algorithms.apf.APFAlgorithm',
    'rl': 'patrol_coordinator.algorithms.rl_nav.RLNavigationAlgorithm',
    'nmopso': 'patrol_coordinator.algorithms.nmopso_nav.NMOPSONavigationAlgorithm',
}


def get_algorithm_class(name: str):
    """Load an algorithm class by name.
    
    Args:
        name: Algorithm name (e.g., 'auction', 'pso', 'apf')
        
    Returns:
        The algorithm class
        
    Raises:
        ValueError: If algorithm name is not registered
    """
    if name not in ALGORITHM_REGISTRY:
        available = ', '.join(sorted(ALGORITHM_REGISTRY.keys()))
        raise ValueError(f"Unknown algorithm '{name}'. Available: {available}")
    
    module_path, class_name = ALGORITHM_REGISTRY[name].rsplit('.', 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
