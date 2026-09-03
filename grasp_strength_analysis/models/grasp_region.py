from dataclasses import dataclass

@dataclass
class GraspRegion:
    start_idx: int
    end_idx: int
    max_force: float
    avg_force: float
    duration: float
    grasp_number: int
