"""BƯỚC 13: Thống kê và Phân tích Người dùng mạng (Audience Stats).
Đọc danh sách 3000 video đã lọc, lấy Top 50 video có view cao nhất,
phân loại view vào các khoảng và sinh báo cáo DOCX, HTML.
"""

import io
import sys

import pandas as pd
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from paths import DATA_DIR, REPORT_DIR, ensure_data_dir, ensure_report_dir

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BINS = [0, 500000, 1000000, 2000000, 3000000, 5000000, float('inf')]
LABELS = [
    "Dưới 500.000",
    "500.000 - 1.000.000",
    "1.000.000 - 2.000.000",
    "2.000.000 - 3.000.000",
    "3.000.000 - 5.000.000",
    "Trên 5.000.000"
]

def _resolve_input_file():
    for name in (
        "v5_3000_videos_filtered.csv",
        "v5_3000_videos_cleaned.csv",
        "v5_3000_videos_raw.csv",
    ):
        path = DATA_DIR / name
        if path.exists():
            return path
    return None

def normalize_view_column(df):
    for col in ['view_count', 'viewCount', 'views', 'ViewCount']:
        if col in df.columns:
            # Chuyển về số (bỏ qua giá trị lỗi)
            df['view_count'] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
    # Nếu không tìm thấy, mặc định tạo cột 0
    df['view_count'] = 0
    return df

def generate_reports(stats_df, total_videos, text_paragraph1, text_paragraph2):
    ensure_report_dir()
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Thống kê người dùng mạng</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
            h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 600px; margin-top: 20px; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .text-content {{ margin-top: 20px; text-indent: 30px; }}
            .bold {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>3.4.5. Người dùng mạng ( phần 传播受众)</h2>
        <p class="text-content">{text_paragraph1}</p>
        
        <p class="bold">Bảng .... Top 50 video hot Youtube về Quan Vũ</p>
        <table>
            <tr>
                <th>Khoảng lượt xem video phổ biến (lượt)</th>
                <th>Số lượng video</th>
                <th>Tỷ lệ phần trăm</th>
            </tr>
    """
    
    for _, row in stats_df.iterrows():
        html_content += f"""
            <tr>
                <td>{row['Khoảng lượt xem video phổ biến (lượt)']}</td>
                <td style="text-align:center;">{row['Số lượng video']}</td>
                <td style="text-align:center;">{row['Tỷ lệ phần trăm']}</td>
            </tr>
        """
        
    html_content += f"""
            <tr>
                <td class="bold">Tổng cộng</td>
                <td class="bold" style="text-align:center;">{total_videos}</td>
                <td class="bold" style="text-align:center;">100%</td>
            </tr>
        </table>
        
        <p class="text-content">{text_paragraph2}</p>
    </body>
    </html>
    """
    
    html_path = REPORT_DIR / "vi" / "report_audience.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_content, encoding='utf-8')
    print(f"[OK] Đã lưu báo cáo HTML tại {html_path}")
    
    # Generate DOCX
    doc = Document()
    
    # Style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Heading
    heading = doc.add_heading('3.4.5. Người dùng mạng ( phần 传播受众)', level=2)
    
    # Para 1
    p1 = doc.add_paragraph(text_paragraph1)
    
    # Table Title
    p_title = doc.add_paragraph("Bảng .... Top 50 video hot Youtube về Quan Vũ")
    p_title.runs[0].bold = True
    
    # Table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Khoảng lượt xem video phổ biến (lượt)'
    hdr_cells[1].text = 'Số lượng video'
    hdr_cells[2].text = 'Tỷ lệ phần trăm'
    
    for _, row in stats_df.iterrows():
        row_cells = table.add_row().cells
        row_cells[0].text = str(row['Khoảng lượt xem video phổ biến (lượt)'])
        row_cells[1].text = str(row['Số lượng video'])
        row_cells[2].text = str(row['Tỷ lệ phần trăm'])
        
    # Footer row
    footer_cells = table.add_row().cells
    footer_cells[0].text = 'Tổng cộng'
    footer_cells[0].paragraphs[0].runs[0].bold = True
    footer_cells[1].text = str(total_videos)
    footer_cells[1].paragraphs[0].runs[0].bold = True
    footer_cells[2].text = '100%'
    footer_cells[2].paragraphs[0].runs[0].bold = True
    
    doc.add_paragraph()
    
    # Para 2
    p2 = doc.add_paragraph(text_paragraph2)
    
    docx_path = REPORT_DIR / "vi" / "report_audience.docx"
    doc.save(str(docx_path))
    print(f"[OK] Đã lưu báo cáo DOCX tại {docx_path}")


def main():
    ensure_data_dir()
    in_file = _resolve_input_file()
    if in_file is None:
        print("[!] Không tìm thấy file video. Chạy step1→step3 trước.")
        return

    df = pd.read_csv(in_file)
    print(f"[*] Đọc {len(df)} video từ {in_file.name}")
    
    # Chuẩn hóa cột view
    df = normalize_view_column(df)
    
    # Lấy top 50 video có view cao nhất
    top_50 = df.nlargest(50, 'view_count').copy()
    
    if len(top_50) == 0:
        print("[!] File dữ liệu không có video nào hoặc thiếu lượt xem.")
        return
        
    # Phân nhóm
    top_50['view_bin'] = pd.cut(top_50['view_count'], bins=BINS, labels=LABELS, right=True)
    
    # Tính số lượng và tỷ lệ
    stats = top_50['view_bin'].value_counts().reindex(LABELS, fill_value=0).reset_index()
    stats.columns = ['Khoảng lượt xem video phổ biến (lượt)', 'Số lượng video']
    stats['Tỷ lệ phần trăm'] = (stats['Số lượng video'] / len(top_50) * 100).apply(lambda x: f"{x:.1f}%" if x > 0 else "0%")
    
    # Tính các biến nội suy cho đoạn văn bản
    most_views_bin = stats.loc[stats['Số lượng video'].idxmax()]
    most_views_range = most_views_bin['Khoảng lượt xem video phổ biến (lượt)']
    most_views_pct = most_views_bin['Tỷ lệ phần trăm']
    
    # Đoạn văn bản
    text_p1 = (
        "Trong thời đại Internet hiện nay, các mạng xã hội mới như YouTube, Facebook, Tiktok "
        "đã trở thành kênh chủ yếu để giới trẻ đương đại truyền tải và tiếp nhận thông tin. "
        "Việc thu thập và tổng hợp số lượt xem và số lượng bình luận của các video liên quan "
        "đến Quan Vũ trên các nền tảng mạng có thể giúp chúng ta hiểu được phần nào tổng quy mô "
        "người xem của các video này. Vì vậy, nghiên cứu đã lựa chọn các video liên quan đến "
        "Quan Vũ trên YouTube, đồng thời lọc ra 50 video có mức độ liên quan và lượt xem "
        "xếp hạng cao nhất để tiến hành thống kê. Sau khi tổng hợp dữ liệu về lượt xem "
        "và số lượng bình luận, kết quả cụ thể được thể hiện trong Bảng...."
    )
    
    text_p2 = (
        f"Theo thống kê trong Bảng … các video liên quan đến Quan Vũ có lượng lượt xem tương đối "
        f"lớn trên nền tảng mạng. Lượt xem của các video chủ yếu phân bố trong khoảng {most_views_range}. "
        f"Trong đó, các video có lượt xem từ {most_views_range} chiếm {most_views_pct} tổng số. "
        "Có thể thấy, mặc dù các video liên quan đến Quan Vũ trên các nền tảng mạng xã hội nước ngoài "
        "có số lượng lượt xem tương đối ấn tượng, thu hút được một lượng khán giả nhất định."
    )
    
    print(f"[*] Thống kê top {len(top_50)} video:")
    print(stats.to_string(index=False))
    
    # Sinh báo cáo
    generate_reports(stats, len(top_50), text_p1, text_p2)
    
    out_csv = DATA_DIR / "v9_audience_stats.csv"
    stats.to_csv(out_csv, index=False, encoding='utf-8-sig')
    print(f"[OK] Đã lưu thống kê raw tại {out_csv.name}")

if __name__ == "__main__":
    main()
