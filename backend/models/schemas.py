"""APIリクエスト・レスポンスのPydanticモデル"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ==========================================
# グリッド計算 API
# ==========================================

class GridPositionRequest(BaseModel):
    """グリッド位置計算リクエスト"""
    rel_x: float = Field(..., ge=0.0, le=1.0, description="X座標の相対位置（0.0-1.0）")
    rel_y: float = Field(..., ge=0.0, le=1.0, description="Y座標の相対位置（0.0-1.0）")
    grid_width: int = Field(..., ge=1, description="グリッドの列数")
    grid_height: int = Field(..., ge=1, description="グリッドの行数")
    video_duration: float = Field(..., gt=0, description="動画の総時間（秒）")
    seconds_per_cell: Optional[float] = Field(None, gt=0, description="1セルあたりの秒数")


class GridPositionResponse(BaseModel):
    """グリッド位置計算レスポンス"""
    timestamp: float
    formatted_time: str
    grid_x: int
    grid_y: int
    grid_index: int
    cell_start_time: float
    cell_end_time: float


class GridConfigRequest(BaseModel):
    """グリッド設定リクエスト"""
    video_duration: float = Field(..., gt=0, description="動画の総時間（秒）")
    columns: int = Field(5, ge=1, le=10, description="列数")
    seconds_per_cell: float = Field(15.0, gt=0, description="マスあたりの秒数")


class GridConfigResponse(BaseModel):
    """グリッド設定レスポンス"""
    rows: int
    columns: int
    total_cells: int
    seconds_per_cell: float
    video_duration: float


# ==========================================
# 動画・サムネイル API
# ==========================================

class VideoUploadResponse(BaseModel):
    """動画アップロードレスポンス"""
    video_id: str
    filename: str
    duration: float
    width: int
    height: int
    video_url: str


class ThumbnailGenerateRequest(BaseModel):
    """サムネイル生成リクエスト"""
    video_id: str
    columns: int = Field(5, ge=1, le=10)
    seconds_per_cell: float = Field(15.0, gt=0)
    thumb_width: int = Field(160, ge=80, le=320)
    thumb_height: int = Field(90, ge=45, le=180)


class ThumbnailGenerateResponse(BaseModel):
    """サムネイル生成レスポンス"""
    video_id: str
    rows: int
    columns: int
    total_cells: int
    seconds_per_cell: float
    duration: float
    thumbnails: List[dict]
