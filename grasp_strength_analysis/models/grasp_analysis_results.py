from dataclasses import dataclass
import numpy as np

@dataclass
class GraspAnalysisResults:
    filename: str

    number_of_grasps: int

    mean: float
    std: float 
    sem: float 
    ts: np.ndarray
    ci: np.ndarray
    pi: np.ndarray
    cv_percent: float 

    cumulative_avg: list[float]
    cumulative_std: list[float]
    cumulative_median: list[float]

    n_required: float 
    n_required_buffer: float 
    moe: float 
    std_dev_interval_lwr: float
    std_dev_interval_upr: float
    n_required_std: float 

