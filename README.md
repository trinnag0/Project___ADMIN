# Scholarship Bridge Admin

A mobile-first Flask administration portal for managing scholarships, students, applications, notifications, and institutional settings.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)

## Features

- Scholarship dashboard with recent activity and application statistics
- Create, edit, view, and delete scholarship opportunities
- Student profiles and application records
- Application status workflow
- Notifications feed
- Mobile-friendly administration interface

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000/admin**

**Demo login:** `admin` / `admin123`

> Change the demo credentials and configure a secure `SECRET_KEY` before production use.

## Deploy to Render

1. Push this repo to GitHub
2. Create a Web Service on Render
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Set `SECRET_KEY` environment variable

## Key screens

- Dashboard
- Scholarship management
- Student profiles
- Application status tabs
- Notifications
- Settings
