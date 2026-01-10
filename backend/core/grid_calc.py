"""
VAMオリジナルロジック（1ミリも狂わず移植）
元: vam5.70/utils/video_utils.py
"""
import math
from typing import Optional, Tuple


def calculate_x_continuous_timestamp(
    rel_x: float,
    rel_y: float,
    grid_width: int,
    grid_height: int,
    video_duration: float,
    seconds_per_cell: Optional[float] = None
) -> float:
    """
    グリッド位置から時刻を計算（X軸連続モード）
    秒/マス情報を使用した正確な計算

    Args:
        rel_x: X座標の相対位置（0.0-1.0）
        rel_y: Y座標の相対位置（0.0-1.0）
        grid_width: グリッドの幅（例：4列）
        grid_height: グリッドの高さ（例：1440行）
        video_duration: 動画の総時間（秒）
        seconds_per_cell: 1セルあたりの秒数（Noneの場合は比例計算）

    Returns:
        再生開始時刻（秒）
    """
    if video_duration <= 0:
        return 0.0

    # seconds_per_cellが指定されている場合は正確な計算
    if seconds_per_cell and seconds_per_cell > 0:
        # Y軸: 行単位で丸める（現状維持）
        row_index = int(rel_y * grid_height)

        # X軸: 連続的な値のまま計算（高精度）
        col_continuous = rel_x * grid_width

        # 連続的なセルインデックスを計算
        continuous_cell_index = row_index * grid_width + col_continuous

        # タイムスタンプを計算
        timestamp = continuous_cell_index * seconds_per_cell

        return max(0.0, min(timestamp, video_duration))

    # seconds_per_cellがない場合は従来の比例計算
    # 正規化された計算（20行ごとの区切り方式）
    RESET_INTERVAL = 20

    current_row = rel_y * grid_height
    actual_row = int(current_row)

    reset_block = actual_row // RESET_INTERVAL
    row_in_block = actual_row % RESET_INTERVAL

    # 区間の開始時刻（比例計算）
    block_start_ratio = (reset_block * RESET_INTERVAL) / grid_height
    block_start_time = block_start_ratio * video_duration

    # 区間内での進行時間
    cells_in_block = row_in_block * grid_width + (rel_x * grid_width)
    max_cells_in_block = RESET_INTERVAL * grid_width
    block_progress_ratio = cells_in_block / max_cells_in_block
    block_duration = (RESET_INTERVAL / grid_height) * video_duration

    timestamp = block_start_time + (block_progress_ratio * block_duration)

    return max(0.0, min(timestamp, video_duration))


def calculate_grid_position(
    click_position: Tuple[float, float],
    grid_size: Tuple[int, int]
) -> Tuple[int, int, int]:
    """
    クリック位置からグリッド座標を計算

    Args:
        click_position: (rel_x, rel_y) 0.0-1.0の相対座標
        grid_size: (grid_width, grid_height)

    Returns:
        (grid_x, grid_y, grid_index)
    """
    rel_x, rel_y = click_position
    grid_width, grid_height = grid_size

    # 両軸とも安全な範囲にクランプ
    safe_rel_x = max(0.0, min(rel_x, 0.9999))
    safe_rel_y = max(0.0, min(rel_y, 0.9999))

    # 安全な整数変換
    grid_x = int(safe_rel_x * grid_width)
    grid_y = int(safe_rel_y * grid_height)

    # 二重の境界チェック
    grid_x = max(0, min(grid_x, grid_width - 1))
    grid_y = max(0, min(grid_y, grid_height - 1))

    # インデックス計算
    grid_index = grid_y * grid_width + grid_x

    # 最終チェック
    max_index = grid_width * grid_height - 1
    if grid_index > max_index or grid_index < 0:
        return grid_x, grid_y, max(0, min(grid_index, max_index))

    return grid_x, grid_y, grid_index


def calculate_grid_dimensions(
    video_duration: float,
    columns: int,
    seconds_per_cell: float
) -> Tuple[int, int, int]:
    """
    動画長からグリッドサイズを計算

    Args:
        video_duration: 動画の長さ（秒）
        columns: 列数
        seconds_per_cell: マスあたりの秒数

    Returns:
        (rows, columns, total_cells)
    """
    total_cells = math.ceil(video_duration / seconds_per_cell)
    rows = math.ceil(total_cells / columns)
    return rows, columns, total_cells


def format_time(seconds: float) -> str:
    """秒を時:分:秒形式にフォーマット"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
    else:
        return f"{minutes:02d}:{secs:05.2f}"
