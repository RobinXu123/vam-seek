"""動画・サムネイル処理ユーティリティ"""
import subprocess
import json
import os
import math
from typing import List
from pathlib import Path


def get_video_info(video_path: str) -> dict:
    """FFprobeで動画情報を取得"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise Exception(f"FFprobe error: {result.stderr}")

        data = json.loads(result.stdout)

        # 動画ストリームを探す
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break

        if not video_stream:
            raise Exception("No video stream found")

        duration = float(data['format'].get('duration', 0))
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))

        return {
            'duration': duration,
            'width': width,
            'height': height,
            'filename': os.path.basename(video_path)
        }
    except subprocess.TimeoutExpired:
        raise Exception("FFprobe timeout")
    except json.JSONDecodeError:
        raise Exception("Failed to parse FFprobe output")


def generate_thumbnails(
    video_path: str,
    output_dir: str,
    video_id: str,
    columns: int = 5,
    seconds_per_cell: float = 15.0,
    thumb_width: int = 160,
    thumb_height: int = 90
) -> List[dict]:
    """FFmpegでサムネイルを生成"""

    # 動画情報取得
    info = get_video_info(video_path)
    duration = info['duration']

    if duration <= 0:
        raise Exception("Invalid video duration")

    # グリッドサイズ計算
    total_cells = math.ceil(duration / seconds_per_cell)

    thumbnails = []

    for i in range(total_cells):
        timestamp = i * seconds_per_cell
        if timestamp >= duration:
            break

        output_file = os.path.join(output_dir, f"{video_id}_{i:04d}.jpg")

        # FFmpegでサムネイル生成
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-vf', f'scale={thumb_width}:{thumb_height}:force_original_aspect_ratio=decrease,pad={thumb_width}:{thumb_height}:(ow-iw)/2:(oh-ih)/2',
            '-q:v', '3',
            output_file
        ]

        try:
            subprocess.run(cmd, capture_output=True, timeout=10)
            if os.path.exists(output_file):
                row = i // columns
                col = i % columns
                thumbnails.append({
                    'index': i,
                    'row': row,
                    'col': col,
                    'timestamp': timestamp,
                    'url': f"/thumbnails/{video_id}_{i:04d}.jpg"
                })
        except subprocess.TimeoutExpired:
            continue

    return thumbnails
