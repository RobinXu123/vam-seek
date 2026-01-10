# VAM Web MVP - 2Dシークマーカー

VAMの核心ロジック「2Dシークマーカー」をWebで体験できるMVPプロトタイプ

## 🎯 これは何？

**グリッドをなぞると時間が変わる！**

動画のサムネイルグリッド上でマウスを動かすと、そのポジションに対応する「再生時間」がリアルタイムで計算されます。これがVAMの核心機能「2Dシークマーカー」です。

## 📁 構成

```
VAM_web/
├── backend/
│   ├── main.py          # FastAPI サーバー
│   └── requirements.txt  # Python依存関係
├── frontend/
│   └── index.html       # React代替のシンプルHTML/JS
└── README.md
```

## 🚀 起動方法

### 1. バックエンド（FastAPI）

```bash
cd backend

# 仮想環境作成（推奨）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 依存関係インストール
pip install -r requirements.txt

# サーバー起動
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. フロントエンド

```bash
cd frontend

# 方法1: Python簡易サーバー
python -m http.server 5173

# 方法2: ファイルを直接ブラウザで開く
# frontend/index.html をダブルクリック
```

### 3. ブラウザでアクセス

- フロントエンド: http://localhost:5173
- API Docs: http://localhost:8000/docs

## 🧪 動作確認

1. バックエンドが起動していると「API接続OK」と表示されます
2. グリッド上でマウスを動かすと：
   - **再生時間**がリアルタイムで更新
   - **グリッド座標**が表示
   - **セルがハイライト**される
3. 設定を変更すると、グリッドが再計算されます

## 🔧 API エンドポイント

### POST /api/grid/position

グリッド座標からタイムスタンプを計算

```json
// リクエスト
{
  "rel_x": 0.5,        // X座標（0.0-1.0）
  "rel_y": 0.3,        // Y座標（0.0-1.0）
  "grid_width": 5,     // 列数
  "grid_height": 48,   // 行数
  "video_duration": 3600,  // 動画長（秒）
  "seconds_per_cell": 15   // 秒/マス
}

// レスポンス
{
  "timestamp": 450.0,
  "formatted_time": "07:30.00",
  "grid_x": 2,
  "grid_y": 14,
  "grid_index": 72,
  "cell_start_time": 1080.0,
  "cell_end_time": 1095.0
}
```

### POST /api/grid/config

グリッド設定を計算

```json
// リクエスト
{
  "video_duration": 3600,
  "columns": 5,
  "seconds_per_cell": 15
}

// レスポンス
{
  "rows": 48,
  "columns": 5,
  "total_cells": 240,
  "seconds_per_cell": 15.0,
  "video_duration": 3600.0
}
```

## 📐 核心アルゴリズム

VAMオリジナルの `calculate_x_continuous_timestamp` を1ミリも狂わず移植：

```python
def calculate_x_continuous_timestamp(rel_x, rel_y, grid_width, grid_height,
                                     video_duration, seconds_per_cell):
    if video_duration <= 0:
        return 0.0

    if seconds_per_cell and seconds_per_cell > 0:
        # Y軸: 行単位で丸める
        row_index = int(rel_y * grid_height)

        # X軸: 連続的な値のまま計算（高精度）
        col_continuous = rel_x * grid_width

        # 連続的なセルインデックスを計算
        continuous_cell_index = row_index * grid_width + col_continuous

        # タイムスタンプを計算
        timestamp = continuous_cell_index * seconds_per_cell

        return max(0.0, min(timestamp, video_duration))
```

## 🎨 次のステップ

1. **動画サムネイル表示** - 実際のグリッド画像を表示
2. **HTML5 Video連携** - シーク位置を実際の動画に反映
3. **WebSocket** - リアルタイム双方向通信
4. **React移行** - コンポーネント分割

## 📚 元コード

- `vam5.70/utils/video_utils.py` - calculate_x_continuous_timestamp
- `vam5.70/gui/preview/core/grid_calculator.py` - GridCalculator
- `vam5.70/core/time_based_grid_calculator.py` - TimeBasedGridCalculator
