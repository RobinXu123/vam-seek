"""グリッド計算APIルーター"""
from fastapi import APIRouter, HTTPException

from core.grid_calc import (
    calculate_x_continuous_timestamp,
    calculate_grid_position,
    calculate_grid_dimensions,
    format_time
)
from models.schemas import (
    GridPositionRequest,
    GridPositionResponse,
    GridConfigRequest,
    GridConfigResponse
)

router = APIRouter(prefix="/api/grid", tags=["grid"])


@router.post("/position", response_model=GridPositionResponse)
async def calculate_position(request: GridPositionRequest):
    """
    グリッド上の相対座標からタイムスタンプを計算
    VAMのcalculate_x_continuous_timestampロジックを完全移植
    """
    try:
        # タイムスタンプ計算（VAMオリジナルロジック）
        timestamp = calculate_x_continuous_timestamp(
            rel_x=request.rel_x,
            rel_y=request.rel_y,
            grid_width=request.grid_width,
            grid_height=request.grid_height,
            video_duration=request.video_duration,
            seconds_per_cell=request.seconds_per_cell
        )

        # グリッド座標計算
        grid_x, grid_y, grid_index = calculate_grid_position(
            click_position=(request.rel_x, request.rel_y),
            grid_size=(request.grid_width, request.grid_height)
        )

        # セルの時間範囲計算
        spc = request.seconds_per_cell or (request.video_duration / (request.grid_width * request.grid_height))
        cell_start_time = grid_index * spc
        cell_end_time = cell_start_time + spc

        return GridPositionResponse(
            timestamp=round(timestamp, 3),
            formatted_time=format_time(timestamp),
            grid_x=grid_x,
            grid_y=grid_y,
            grid_index=grid_index,
            cell_start_time=round(cell_start_time, 3),
            cell_end_time=round(cell_end_time, 3)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=GridConfigResponse)
async def calculate_grid_config(request: GridConfigRequest):
    """
    グリッド設定を計算
    動画の長さから必要なグリッドサイズを計算
    """
    try:
        rows, columns, total_cells = calculate_grid_dimensions(
            video_duration=request.video_duration,
            columns=request.columns,
            seconds_per_cell=request.seconds_per_cell
        )

        return GridConfigResponse(
            rows=rows,
            columns=columns,
            total_cells=total_cells,
            seconds_per_cell=request.seconds_per_cell,
            video_duration=request.video_duration
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
