"""動画・サムネイルAPIルーター"""
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from core.grid_calc import calculate_grid_dimensions
from core.video_utils import get_video_info, generate_thumbnails
from models.schemas import (
    VideoUploadResponse,
    ThumbnailGenerateRequest,
    ThumbnailGenerateResponse
)

router = APIRouter(prefix="/api/video", tags=["video"])

# 作業ディレクトリ（main.pyからインポート時に設定される）
UPLOAD_DIR: Path = None
THUMBNAIL_DIR: Path = None


def init_dirs(upload_dir: Path, thumbnail_dir: Path):
    """ディレクトリを初期化"""
    global UPLOAD_DIR, THUMBNAIL_DIR
    UPLOAD_DIR = upload_dir
    THUMBNAIL_DIR = thumbnail_dir


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """動画ファイルをアップロード"""

    # ファイル拡張子チェック
    allowed_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mov'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # ユニークIDを生成
    video_id = str(uuid.uuid4())[:8]
    filename = f"{video_id}{ext}"
    filepath = UPLOAD_DIR / filename

    # ファイル保存
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 動画情報取得
    try:
        info = get_video_info(str(filepath))
    except Exception as e:
        # 失敗したらファイル削除
        filepath.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid video file: {str(e)}")

    return VideoUploadResponse(
        video_id=video_id,
        filename=file.filename,
        duration=info['duration'],
        width=info['width'],
        height=info['height'],
        video_url=f"/uploads/{filename}"
    )


@router.post("/thumbnails", response_model=ThumbnailGenerateResponse)
async def generate_video_thumbnails(request: ThumbnailGenerateRequest):
    """動画からサムネイルを生成"""

    # 動画ファイルを探す
    video_path = None
    for ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
        candidate = UPLOAD_DIR / f"{request.video_id}{ext}"
        if candidate.exists():
            video_path = candidate
            break

    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")

    # 動画情報取得
    try:
        info = get_video_info(str(video_path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # サムネイル生成
    try:
        thumbnails = generate_thumbnails(
            video_path=str(video_path),
            output_dir=str(THUMBNAIL_DIR),
            video_id=request.video_id,
            columns=request.columns,
            seconds_per_cell=request.seconds_per_cell,
            thumb_width=request.thumb_width,
            thumb_height=request.thumb_height
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")

    # グリッドサイズ計算
    rows, columns, total_cells = calculate_grid_dimensions(
        video_duration=info['duration'],
        columns=request.columns,
        seconds_per_cell=request.seconds_per_cell
    )

    return ThumbnailGenerateResponse(
        video_id=request.video_id,
        rows=rows,
        columns=columns,
        total_cells=len(thumbnails),
        seconds_per_cell=request.seconds_per_cell,
        duration=info['duration'],
        thumbnails=thumbnails
    )


@router.get("/{video_id}/info")
async def get_video_info_api(video_id: str):
    """動画情報を取得"""

    # 動画ファイルを探す
    video_path = None
    video_ext = None
    for ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
        candidate = UPLOAD_DIR / f"{video_id}{ext}"
        if candidate.exists():
            video_path = candidate
            video_ext = ext
            break

    if not video_path:
        raise HTTPException(status_code=404, detail="Video not found")

    try:
        info = get_video_info(str(video_path))
        info['video_id'] = video_id
        info['video_url'] = f"/uploads/{video_id}{video_ext}"
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """動画とサムネイルを削除"""

    deleted_files = []

    # 動画ファイル削除
    for ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
        video_file = UPLOAD_DIR / f"{video_id}{ext}"
        if video_file.exists():
            video_file.unlink()
            deleted_files.append(str(video_file))

    # サムネイル削除
    for thumb_file in THUMBNAIL_DIR.glob(f"{video_id}_*.jpg"):
        thumb_file.unlink()
        deleted_files.append(str(thumb_file))

    return {"deleted": deleted_files, "count": len(deleted_files)}
