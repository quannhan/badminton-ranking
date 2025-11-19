# =====================================================
# FILE: app/utils/scoring.py
# =====================================================

def calculate_points(stake_value: int, result: str) -> int:
    """
    Tính điểm dựa trên mức độ và kết quả
    - Thắng: stake_value * 10
    - Thua: stake_value * 5
    """
    if result == "WIN":
        return stake_value * 10
    elif result == "LOSE":
        return stake_value * 5
    return 0