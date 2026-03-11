from dataclasses import dataclass

@dataclass
class InitializationAngle:
    starting_angle: float 
    angle_increment: float 
    trials_per_angle: int

    angles: list[float]
    avg_forces_by_angle: list[float]
    max_angle: float 
    max_force: float 