# GR-Pilot Deployment Guide

Toyota GR Cup Series - Racing Analytics Platform

## 📋 Ön Hazırlık

### Gerekli Hesaplar:
1. **GitHub** hesabı (kod için)
2. **Vercel** hesabı (frontend için) - [vercel.com](https://vercel.com)
3. **Render** hesabı (backend için) - [render.com](https://render.com)

Her ikisi de **ücretsiz** plan sunuyor ve kredi kartı gerektirmiyor.

---

## 🚀 Seçenek 1: Vercel + Render (Önerilen - En Kolay)

### A) Backend Deployment (Render)

1. **Render'a giriş yapın**: [dashboard.render.com](https://dashboard.render.com)

2. **New Web Service** butonuna tıklayın

3. GitHub repo'nuzu bağlayın:
   - "Connect a repository" seçeneğini seçin
   - GitHub'da authorize edin
   - Bu repo'yu seçin

4. **Ayarları yapılandırın**:
   ```
   Name: gr-pilot-backend
   Region: Frankfurt (veya en yakın)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Environment Variables** ekleyin:
   - `GROQ_API_KEY`: Groq API anahtarınız
   - `PYTHON_VERSION`: 3.11.0

6. **Create Web Service** butonuna tıklayın

7. Deploy tamamlandığında URL'yi kopyalayın (örn: `https://gr-pilot-backend.onrender.com`)

### B) Frontend Deployment (Vercel)

1. **Vercel'e giriş yapın**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Add New Project** butonuna tıklayın

3. GitHub repo'nuzu import edin

4. **Ayarları yapılandırın**:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

5. **Environment Variables** ekleyin:
   ```
   VITE_API_URL: https://gr-pilot-backend.onrender.com (Render'dan aldığınız URL)
   ```

6. **Deploy** butonuna tıklayın

7. Deploy tamamlandığında size bir URL verilecek (örn: `https://gr-pilot.vercel.app`)

✅ **Tamamlandı!** Artık projeniz online!

---

## 🐳 Seçenek 2: Docker ile Local/Cloud Deploy

### Local'de Test:

```bash
# Projenin ana dizininde
docker-compose up --build

# Tarayıcıda açın:
# Frontend: http://localhost:80
# Backend: http://localhost:8000
```

### Docker Hub'a Push:

```bash
# Backend
cd backend
docker build -t yourusername/gr-pilot-backend:latest .
docker push yourusername/gr-pilot-backend:latest

# Frontend
cd ../frontend
docker build -t yourusername/gr-pilot-frontend:latest .
docker push yourusername/gr-pilot-frontend:latest
```

---

## 🌐 Seçenek 3: Railway (Tek Platform)

1. **Railway'e giriş yapın**: [railway.app](https://railway.app)

2. **New Project** → **Deploy from GitHub repo**

3. **Backend** için:
   - Root directory: `backend`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment variables: `GROQ_API_KEY`

4. **Frontend** için:
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Start command: `npm run preview`
   - Environment variables: `VITE_API_URL` (backend URL'si)

---

## 📝 Deploy Sonrası Kontroller

### Backend Health Check:
```bash
curl https://your-backend-url.com/health
```

Beklenen yanıt:
```json
{"status": "healthy"}
```

### Frontend Test:
1. Tarayıcıda frontend URL'nizi açın
2. Onboarding modal'ı görünmeli
3. Training sekmesine gidin
4. Lap seçin ve verilerin yüklendiğini kontrol edin

---

## 🔧 Sorun Giderme

### Backend 500 Error:
- Render logs'u kontrol edin: Dashboard → Service → Logs
- `GROQ_API_KEY` doğru ayarlandı mı?
- Requirements.txt tüm bağımlılıkları içeriyor mu?

### Frontend API Hatası:
- `VITE_API_URL` doğru mu?
- CORS ayarları backend'de aktif mi? (main.py içinde)
- Backend'in HTTPS kullanıyorsa, frontend de HTTPS kullanmalı

### Docker Build Hatası:
```bash
# Cache'i temizle
docker system prune -a

# Tekrar build et
docker-compose build --no-cache
```

---

## 🎯 Üretim İyileştirmeleri

### 1. Environment Variables:
Backend `.env` dosyasını düzenleyin:
```
GROQ_API_KEY=your_key_here
DATABASE_URL=postgresql://...  # İleride DB eklerseniz
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### 2. CORS Güvenliği:
`backend/main.py` içinde:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",  # Production URL
        "http://localhost:5173"  # Development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting:
Backend'e rate limiter ekleyin (DDoS koruması)

### 4. Monitoring:
- Render: Built-in logs ve metrics
- Vercel: Analytics dashboard
- Sentry.io: Error tracking (ücretsiz)

---

## 📊 Deployment Özeti

| Platform | Frontend | Backend | Ücretsiz? | Süre |
|----------|----------|---------|-----------|------|
| **Vercel + Render** | ✅ | ✅ | Evet | 5-10 dk |
| **Railway** | ✅ | ✅ | Evet | 5-10 dk |
| **Docker Local** | ✅ | ✅ | Evet | 2-5 dk |
| **Docker Cloud** | ✅ | ✅ | Kısmi | 10-15 dk |

---

## 🎉 Başarılı Deploy!

Projeniz artık online! URL'leri Toyota hackathon jürisine gönderin:

- **Frontend**: `https://gr-pilot.vercel.app`
- **Backend API**: `https://gr-pilot-backend.onrender.com`
- **Docs**: `https://gr-pilot-backend.onrender.com/docs`

---

## 🆘 Yardım

Deploy sırasında sorun yaşarsanız:
1. Logs'ları kontrol edin
2. Environment variables'ı doğrulayın
3. GitHub Actions'ı kontrol edin
4. Community: [Vercel Discord](https://vercel.com/discord) | [Render Community](https://community.render.com)
