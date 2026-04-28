"""BƯỚC 2 (V5): Lọc video (Hybrid Approach).
Lọc các video từ v5_3000_videos_raw.csv:
- Level 1: Lọc bằng hệ thống Keyword Scoring.
- Level 2: Các video rớt Level 1 sẽ được AI Embeddings chấm điểm.
- Chỉ loại bỏ các video thực sự không liên quan.
"""

import pandas as pd
from pathlib import Path
import warnings

# Tắt các warning của thư viện
warnings.filterwarnings('ignore')

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Trọng số từ khóa
MAIN_KEYS = [
    "quan vũ", "quan công", "quan vân trường", "quan thánh", 
    "guan yu", "关羽", "võ thánh", "nhị ca"
]

RELATED_KEYS = [
    "tam quốc", "thục hán", "lưu bị", "trương phi", "tào tháo", 
    "thanh long yển nguyệt đao", "xích thố", "ngũ hổ tướng", "triệu vân", 
    "gia cát lượng", "khổng minh", "lã bố", "điêu thuyền", "đổng trác", "ba anh em"
]

def score_by_keywords(title):
    if not isinstance(title, str):
        return 0
    title_lower = title.lower()
    score = 0
    
    # 5 điểm cho từ khóa chính
    for key in MAIN_KEYS:
        if key in title_lower:
            score += 5
            
    # 2 điểm cho từ khóa phụ
    for key in RELATED_KEYS:
        if key in title_lower:
            score += 2
            
    return score

def get_sentence_model():
    try:
        from sentence_transformers import SentenceTransformer, util
        # Dùng model nhẹ, hỗ trợ tiếng Việt
        print("[*] Đang tải mô hình AI Embeddings (paraphrase-multilingual-MiniLM-L12-v2)...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        return model, util
    except ImportError:
        print("[!] LỖI: Chưa cài thư viện AI. Hãy chạy: pip install sentence-transformers")
        print("[!] Tạm thời sẽ chỉ lọc bằng Keywords (Level 1).")
        return None, None

def main():
    in_file = DATA_DIR / "v5_3000_videos_raw.csv"
    out_file = DATA_DIR / "v5_3000_videos_filtered.csv"
    
    if not in_file.exists():
        print(f"[!] Không tìm thấy file {in_file}")
        return

    df = pd.read_csv(in_file)
    initial_count = len(df)
    print(f"[*] Đọc {initial_count} videos từ {in_file.name}")

    # Xóa dòng null title
    df = df.dropna(subset=['title']).copy()
    
    # LEVEL 1: Lọc qua Keyword Scoring
    KEYWORD_THRESHOLD = 2
    
    print("[*] LEVEL 1: Đang lọc qua Keyword Scoring...")
    df['keyword_score'] = df['title'].apply(score_by_keywords)
    
    df_passed_level1 = df[df['keyword_score'] >= KEYWORD_THRESHOLD].copy()
    df_failed_level1 = df[df['keyword_score'] < KEYWORD_THRESHOLD].copy()
    
    print(f"  -> Đạt điểm Keyword: {len(df_passed_level1)} videos.")
    print(f"  -> Bị loại khỏi Level 1: {len(df_failed_level1)} videos.")
    
    # LEVEL 2: Lọc qua AI Embeddings (Chỉ quét các video rớt Level 1)
    df_passed_level2 = pd.DataFrame()
    if not df_failed_level1.empty:
        model, util = get_sentence_model()
        if model is not None:
            AI_THRESHOLD = 0.35 # Ngưỡng tương đồng Cosine
            print(f"[*] LEVEL 2: Dùng AI quét {len(df_failed_level1)} videos bị loại ở Level 1...")
            
            # Câu neo chuẩn
            anchor_sentence = "Video phân tích lịch sử, nhân vật Quan Vũ, Quan Công, Quan Vân Trường, Lưu Bị, Trương Phi, Tào Tháo trong phim Tam Quốc Diễn Nghĩa"
            anchor_emb = model.encode(anchor_sentence, convert_to_tensor=True)
            
            # Encode tất cả title của video bị loại
            titles_to_check = df_failed_level1['title'].tolist()
            title_embs = model.encode(titles_to_check, convert_to_tensor=True, show_progress_bar=True)
            
            # Tính Cosine Similarity
            cosine_scores = util.cos_sim(anchor_emb, title_embs)[0]
            df_failed_level1['ai_score'] = cosine_scores.cpu().numpy()
            
            # Lọc những video đạt ngưỡng AI
            df_passed_level2 = df_failed_level1[df_failed_level1['ai_score'] >= AI_THRESHOLD].copy()
            print(f"  -> AI cứu vớt thành công: {len(df_passed_level2)} videos.")
    
    # Gộp kết quả
    if not df_passed_level2.empty:
        final_df = pd.concat([df_passed_level1, df_passed_level2], ignore_index=True)
    else:
        final_df = df_passed_level1
    
    # Sắp xếp lại: ưu tiên điểm keyword cao, nếu có ai_score thì cũng cho lên trên
    # Gán điểm ai_score = 0 cho những video passed level 1 để tránh lỗi NaN
    if 'ai_score' not in final_df.columns:
        final_df['ai_score'] = 0.0
    else:
        final_df['ai_score'] = final_df['ai_score'].fillna(0.0)
        
    final_df = final_df.sort_values(by=['keyword_score', 'ai_score'], ascending=[False, False])
    
    # Xóa các cột tạm để trả về đúng format schema ban đầu
    final_df = final_df.drop(columns=['keyword_score', 'ai_score'])
        
    filtered_count = len(final_df)
    print(f"\n[*] TỔNG KẾT: Giữ lại {filtered_count} videos (Đã loại bỏ hẳn {initial_count - filtered_count} videos).")
    
    final_df.to_csv(out_file, index=False, encoding='utf-8-sig')
    print(f"[OK] Đã lưu vào {out_file.name}")

if __name__ == "__main__":
    main()
