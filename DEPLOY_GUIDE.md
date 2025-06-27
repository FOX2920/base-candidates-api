# 🚀 Hướng dẫn Deploy API lên Vercel

## 📋 Chuẩn bị

### 1. Tạo tài khoản Vercel

- Truy cập [vercel.com](https://vercel.com)
- Đăng ký bằng GitHub account

### 2. Cài đặt Vercel CLI

```bash
npm install -g vercel
```

## 🔧 Các files cần thiết (đã tạo sẵn)

✅ `vercel.json` - Cấu hình Vercel  
✅ `requirements.txt` - Python dependencies  
✅ `api_wrapper.py` - Flask API đã được cấu hình cho Vercel  
✅ `.gitignore` - Loại trừ files không cần thiết

## 🚀 Phương pháp 1: Deploy qua Vercel CLI (Khuyến nghị)

### Bước 1: Login Vercel

```bash
vercel login
```

### Bước 2: Deploy từ terminal

```bash
# Trong thư mục project
vercel
```

### Bước 3: Làm theo hướng dẫn

```
? Set up and deploy "~/New folder (2)"? [Y/n] Y
? Which scope do you want to deploy to? [Chọn account của bạn]
? Link to existing project? [N/y] N
? What's your project's name? base-candidates-api
? In which directory is your code located? ./
```

### Bước 4: Deploy production

```bash
vercel --prod
```

## 🌐 Phương pháp 2: Deploy qua GitHub + Vercel Dashboard

### Bước 1: Push code lên GitHub

```bash
# Khởi tạo git repository
git init

# Add files
git add .
git commit -m "Initial commit: Base Candidates API"

# Tạo repository trên GitHub và push
git remote add origin https://github.com/yourusername/base-candidates-api.git
git push -u origin main
```

### Bước 2: Connect với Vercel

1. Vào [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import GitHub repository
4. Vercel sẽ tự động detect là Python project

### Bước 3: Cấu hình Environment Variables (nếu cần)

- Vào Project Settings → Environment Variables
- Thêm `BASE_API_KEY` nếu muốn bảo mật API key

## 🧪 Test API sau khi deploy

### Lấy URL từ Vercel

Sau khi deploy thành công, bạn sẽ có URL dạng:

```
https://base-candidates-api-xxx.vercel.app
```

### Test các endpoints

#### 1. Health check

```bash
curl https://your-app.vercel.app/health
```

#### 2. Get job openings

```bash
curl https://your-app.vercel.app/job-openings
```

#### 3. Get candidates

```bash
curl "https://your-app.vercel.app/candidates?opening_id=9165"
```

#### 4. Get stages

```bash
curl "https://your-app.vercel.app/stages?opening_id=9165"
```

## 🔧 Cập nhật OpenAPI Schema cho Custom GPT

Sau khi có URL Vercel, cập nhật file `openapi_schema.json`:

```json
{
  "servers": [
    {
      "url": "https://your-app.vercel.app",
      "description": "Production server"
    }
  ]
}
```

## 🎯 Cấu hình Custom GPT

### Bước 1: Tạo Custom GPT

1. Vào ChatGPT → Create a GPT
2. Configure → Actions
3. Copy nội dung từ `openapi_schema.json` (đã cập nhật URL)

### Bước 2: Instructions cho GPT

```
Bạn là AI HR Assistant chuyên nghiệp có thể:

🔍 **Tìm kiếm candidates**: Sử dụng getCandidates(opening_id, stage_ids)
📋 **Xem job openings**: Sử dụng getJobOpenings()
📊 **Phân tích stages**: Sử dụng getStages(opening_id)

**Cách sử dụng:**
- "Lấy danh sách candidates cho vị trí 9165"
- "Tìm candidates ở giai đoạn nhận hồ sơ"
- "Phân tích profile của ứng viên"

Luôn trả lời bằng tiếng Việt và format thông tin dễ đọc.
```

### Bước 3: Test Custom GPT

- "Lấy danh sách job openings"
- "Tìm candidates cho vị trí Management Trainee"
- "Phân tích giai đoạn tuyển dụng"

## 🔒 Security & Performance

### Environment Variables

```bash
# Thêm vào Vercel Project Settings
BASE_API_KEY=your_secure_api_key
```

### Rate Limiting (nếu cần)

```python
# Thêm vào api_wrapper.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

## 🐛 Troubleshooting

### Lỗi thường gặp:

#### 1. Import error

```
Error: Cannot find module 'main'
```

**Giải pháp:** Đảm bảo `main.py` và `api_wrapper.py` cùng thư mục

#### 2. API key error

```
Error: BASE_API_KEY not found
```

**Giải pháp:** Thêm API key vào Environment Variables

#### 3. CORS error

```
CORS policy error
```

**Giải pháp:** `flask-cors` đã được cài đặt, kiểm tra cấu hình

### Xem logs:

```bash
vercel logs your-deployment-url
```

## 🎉 Kết quả mong đợi

Sau khi hoàn thành, bạn sẽ có:

✅ **API URL sống trên Vercel**: `https://your-app.vercel.app`  
✅ **Custom GPT kết nối được với API**  
✅ **Có thể hỏi về candidates real-time**  
✅ **Auto-deploy khi push code mới**

**Custom GPT của bạn sẽ trở thành HR Assistant thông minh!** 🚀

## 📞 Support

Nếu gặp vấn đề:

1. Check Vercel deployment logs
2. Test API endpoints manual trước
3. Verify OpenAPI schema syntax
4. Check Custom GPT Actions configuration
