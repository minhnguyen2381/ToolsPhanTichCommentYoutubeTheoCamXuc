# Cài Đặt Chi Tiết

Tài liệu này hướng dẫn cài đặt đầy đủ môi trường cho dự án.

---

## 1. Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu | Ghi chú |
|------------|---------------------|---------|
| Python | 3.10+ | Khuyến nghị 3.10 hoặc 3.11 |
| pip | 23.0+ | `python -m pip install --upgrade pip` |
| Git | 2.30+ | Để clone repo |
| RAM | 4 GB | 8 GB nếu chạy PhoBERT trên CPU |
| GPU (tuỳ chọn) | CUDA 11.8+ | Tăng tốc sentiment 10–20 lần |

---

## 2. Tạo môi trường ảo (venv)

### Windows (PowerShell)
```powershell
cd D:\DuAn\ToolsPhanTichCommentYoutube
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows (Git Bash)
```bash
cd /d/DuAn/ToolsPhanTichCommentYoutube
python -m venv .venv
source .venv/Scripts/activate
```

### Linux / macOS
```bash
cd ~/ToolsPhanTichCommentYoutube
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Cài thư viện

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Nếu lỗi khi cài `torch` trên Windows, thử bản CPU-only:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

GPU CUDA 11.8:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## 4. Cấu hình `.env`

Pipeline **không cần API key**: dữ liệu YouTube được lấy qua `yt-dlp` và `youtube-comment-downloader` (thư viện cào dữ liệu công khai, không tính quota).

```bash
cp .env.example .env
# Mở .env, sửa PLAYLIST_ID nếu cần
```

Biến duy nhất: `PLAYLIST_ID` (tuỳ chọn, mặc định lấy playlist trong source code).

---

## 5. Kiểm tra nhanh

```bash
python -c "from src.youtube_client import search_videos; print(search_videos('Quan Vũ', 3))"
```

Nếu in ra danh sách 3 videoId là thành công.

---

## 6. Lần chạy PhoBERT đầu tiên

Lần đầu chạy `step3_sentiment.py`, thư viện `transformers` sẽ download model (~500 MB) từ HuggingFace về cache `~/.cache/huggingface/`. Cần internet. Các lần sau chạy offline được.

---

## 7. Troubleshooting

Xem [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
