# Scholarship Bridge Admin

Mobile-first admin portal for managing scholarships, students, and applications.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000/admin**

**Login:** `admin` / `admin123`

## Deploy to Render

1. Push this repo to GitHub
2. Create a Web Service on Render
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Set `SECRET_KEY` environment variable

## Screens

- Dashboard with stats & recent scholarships
- Scholarships list, add, edit, delete, details
- Students list & profiles
- Applications with status tabs
- Notifications feed
- Settings & More menu
