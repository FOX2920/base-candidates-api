from flask import Flask, request, jsonify
from flask_cors import CORS
from main import get_candidates_data, get_base_openings, get_opening_stages
import os

app = Flask(__name__)
CORS(app)

# Lấy API key từ environment
BASE_API_KEY = '5654-PTE7TTHBUKSU5W8XT2T3QDHRN7Y463A3T6ZDDP7DK95EZJBWSRLNLFKZNWKQGED4-FXYJZT6CBF89EEV2QYMNNDZZ7BSBU8KXJZTJJ643XZS8AWWBHUEE47MMAKC6GCRC'

@app.route('/candidates', methods=['GET'])
def get_candidates():
    """API endpoint để Custom GPT gọi lấy thông tin candidates"""
    try:
        opening_id = request.args.get('opening_id')
        stage_ids_str = request.args.get('stage_ids', '')
        
        if not opening_id:
            return jsonify({"error": "opening_id is required"}), 400
        
        # Parse stage_ids nếu có
        stage_ids = None
        if stage_ids_str:
            stage_ids = [int(id.strip()) for id in stage_ids_str.split(',') if id.strip()]
        
        # Lấy dữ liệu candidates
        candidates_df = get_candidates_data(opening_id, BASE_API_KEY, stage_ids)
        
        if candidates_df.empty:
            return jsonify({"candidates": [], "total": 0})
        
        # Convert DataFrame to JSON
        candidates_list = candidates_df.to_dict('records')
        
        # Format response for Custom GPT
        response = {
            "candidates": candidates_list,
            "total": len(candidates_list),
            "opening_id": opening_id,
            "message": f"Đã tìm thấy {len(candidates_list)} ứng viên"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/job-openings', methods=['GET'])
def get_job_openings():
    """API endpoint để lấy danh sách job openings"""
    try:
        openings_df = get_base_openings(BASE_API_KEY)
        
        if openings_df.empty:
            return jsonify({"openings": [], "total": 0})
        
        openings_list = openings_df.to_dict('records')
        
        response = {
            "openings": openings_list,
            "total": len(openings_list),
            "message": f"Đã tìm thấy {len(openings_list)} vị trí tuyển dụng"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stages', methods=['GET'])
def get_stages():
    """API endpoint để lấy danh sách stages của một opening"""
    try:
        opening_id = request.args.get('opening_id')
        
        if not opening_id:
            return jsonify({"error": "opening_id is required"}), 400
        
        stages_df = get_opening_stages(opening_id, BASE_API_KEY)
        
        if stages_df.empty:
            return jsonify({"stages": [], "total": 0})
        
        stages_list = stages_df.to_dict('records')
        
        response = {
            "stages": stages_list,
            "total": len(stages_list),
            "opening_id": opening_id,
            "message": f"Đã tìm thấy {len(stages_list)} giai đoạn tuyển dụng"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API đang hoạt động bình thường"})

# Export app for Vercel
app.config['ENV'] = 'production'

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 