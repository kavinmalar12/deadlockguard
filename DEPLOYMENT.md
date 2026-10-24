# 🚀 DeadlockGuard — Publishing & Deployment Guide

DeadlockGuard is built from the ground up to be **100% cloud-native and deployable in under 2 minutes** across multiple platforms with zero cost.

---

## 🌐 Method 1: Streamlit Community Cloud (Recommended & Free)
*Best for: Instant public sharing, student project submissions, live instructor demos.*

1. **Create a GitHub Repository**:
   - Push your `deadlock_guard` folder to a new GitHub repository (e.g. `https://github.com/your-username/deadlockguard`).
   ```bash
   git init
   git add .
   git commit -m "Initial commit of DeadlockGuard"
   git branch -M main
   git remote add origin https://github.com/<your-username>/deadlockguard.git
   git push -u origin main
   ```
2. **Sign in to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and click **Sign in with GitHub**.
3. **Deploy with 1 Click**:
   - Click **New app**.
   - Select your repository (`deadlockguard`), branch (`main`), and set Main file path to: `app.py`.
   - Click **Deploy!**
4. **Done!** Your app is immediately live with a permanent public link:
   `https://<your-username>-deadlockguard.streamlit.app`

---

## 🤗 Method 2: Hugging Face Spaces (Free Cloud Hosting)
*Best for: AI/ML portfolio showcase with dedicated CPU & 16GB RAM.*

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select **Space SDK**: **Streamlit**.
3. Set Space hardware to **Free CPU (2 vCPU, 16GB RAM)**.
4. Clone the repository and copy all DeadlockGuard files into it:
   ```bash
   git clone https://huggingface.co/spaces/<your-username>/deadlockguard
   cp -r /path/to/deadlock_guard/* deadlockguard/
   cd deadlockguard
   git add .
   git commit -m "Deploy DeadlockGuard"
   git push
   ```
5. Hugging Face will automatically build and host the interactive web app at:
   `https://huggingface.co/spaces/<your-username>/deadlockguard`

---

## 🐳 Method 3: Docker Container (Local or Cloud Server)
*Best for: AWS ECS, GCP Cloud Run, Azure App Service, DigitalOcean, or private enterprise servers.*

### Run Locally with Docker
```bash
# Build the production container image
docker build -t deadlockguard:latest .

# Run the container mapping port 8501
docker run -d -p 8501:8501 --name deadlockguard-app deadlockguard:latest
```
Open your browser to: **`http://localhost:8501`**

### Run with Docker Compose
```bash
docker-compose up -d
```

### Deploy to GCP Cloud Run
```bash
gcloud run deploy deadlockguard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## ☁️ Method 4: Render / Railway / Fly.io (PaaS 1-Click)
DeadlockGuard includes pre-configured [`render.yaml`](file:///C:/Users/kavin/.gemini/antigravity/scratch/deadlock_guard/render.yaml) and [`Procfile`](file:///C:/Users/kavin/.gemini/antigravity/scratch/deadlock_guard/Procfile):

1. **Render**:
   - Go to [render.com](https://render.com/).
   - Click **New Web Service** and connect your GitHub repository.
   - Render will automatically detect `render.yaml` or Python settings, build dependencies, and launch.
2. **Railway**:
   - Go to [railway.app](https://railway.app/).
   - Click **New Project** -> **Deploy from GitHub repo**.
   - It will auto-detect Streamlit via `Procfile` and launch on a custom public domain.

---

## 🧪 CI/CD Automated Testing
Every git commit triggers the GitHub Actions workflow in [`.github/workflows/ci.yml`](file:///C:/Users/kavin/.gemini/antigravity/scratch/deadlock_guard/.github/workflows/ci.yml):
- Verifies python compatibility (3.10 & 3.11).
- Installs dependencies.
- Runs all 14 correctness and detection checks automatically.
