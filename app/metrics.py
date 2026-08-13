from typing import Optional

def compute_ratio(active: int, total: int) -> Optional[float]:
    if total == 0:
        return None  # or any other suitable default value
    return active / total