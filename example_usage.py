"""
Ví dụ sử dụng code để lấy thông tin candidates từ Base API
"""

import os
from main import get_candidates_data, get_base_openings, get_opening_stages

def demo_usage():
    """Demo cách sử dụng các functions chính"""
    
    print("📋 DEMO SỬ DỤNG CODE LẤY THÔNG TIN CANDIDATES")
    print("=" * 50)
    
    # Lấy API key từ environment variable
    access_token = os.getenv('BASE_API_KEY')
    
    if not access_token:
        print("⚠️  Cần thiết lập BASE_API_KEY trong environment variable để test với API thực")
        print("💡 Ví dụ: set BASE_API_KEY=your_api_key_here")
        print("\n📝 Để test, bạn có thể:")
        print("1. Tạo file .env với nội dung: BASE_API_KEY=your_actual_api_key")
        print("2. Hoặc set environment variable trong terminal")
        print("\n🔧 Các functions chính đã sẵn sàng sử dụng:")
        print_available_functions()
        return
    
    try:
        print("🔍 Đang lấy danh sách job openings...")
        job_openings = get_base_openings(access_token)
        
        if job_openings.empty:
            print("❌ Không tìm thấy job openings nào")
            return
        
        print(f"✅ Tìm thấy {len(job_openings)} job openings:")
        print(job_openings)
        
        # Lấy opening đầu tiên để demo
        opening_id = job_openings['id'].iloc[0]
        opening_name = job_openings['name'].iloc[0]
        
        print(f"\n🎯 Đang lấy thông tin cho position: {opening_name}")
        print(f"📋 Opening ID: {opening_id}")
        
        # Lấy danh sách stages
        print("\n📊 Đang lấy danh sách stages...")
        stages_df = get_opening_stages(opening_id, access_token)
        if not stages_df.empty:
            print("✅ Các stages hiện có:")
            print(stages_df)
        
        # Lấy thông tin candidates
        print("\n👥 Đang lấy thông tin candidates...")
        candidates_df = get_candidates_data(opening_id, access_token)
        
        if candidates_df.empty:
            print("❌ Không tìm thấy candidates nào")
            return
        
        print(f"✅ Đã lấy thông tin {len(candidates_df)} candidates")
        print(f"📋 Columns: {list(candidates_df.columns)}")
        print(f"\n📊 Sample data:")
        print(candidates_df.head())
        
        # Lưu vào file CSV
        output_file = f"candidates_{opening_id}.csv"
        candidates_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 Đã lưu dữ liệu vào file: {output_file}")
        
        print("\n🎉 Demo hoàn thành thành công!")
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy demo: {str(e)}")

def print_available_functions():
    """In ra danh sách các functions có sẵn"""
    print("📚 CÁC FUNCTIONS CHỦ YẾU:")
    print("-" * 30)
    
    functions_info = [
        ("get_base_openings(access_token)", "Lấy danh sách job openings"),
        ("get_opening_stages(opening_id, access_token)", "Lấy các stages của một job"),
        ("get_candidates_data(opening_id, access_token, stage_ids)", "Lấy thông tin candidates"),
        ("fetch_candidates_by_stages(opening_id, access_token)", "Lấy raw data từ API"),
        ("process_data(raw_data)", "Xử lý raw data thành DataFrame"),
        ("fetch_jd(opening_id, access_token)", "Lấy job description")
    ]
    
    for func, desc in functions_info:
        print(f"• {func}")
        print(f"  └─ {desc}")
        print()
    
    print("💡 CÁCH SỬ DỤNG CƠ BẢN:")
    print("-" * 20)
    print("""
# 1. Import functions
from main import get_candidates_data, get_base_openings

# 2. Lấy danh sách job openings
openings = get_base_openings(access_token)

# 3. Lấy candidates cho một opening cụ thể
candidates_df = get_candidates_data(opening_id, access_token)

# 4. Lưu kết quả
candidates_df.to_csv('candidates.csv', index=False, encoding='utf-8-sig')
""")

if __name__ == "__main__":
    demo_usage() 