# 🦖 Aditi - Your Pharmaceutical Assistant

## 📈 Project Overview

**Aditi** is a Flask-based web application that serves as your AI-powered pharmaceutical assistant. It provides:

- Clinical drug information, including therapeutic uses, dosage guidelines, side effects, contraindications, and drug interactions.
- Symptom-based drug recommendations following evidence-based guidelines.
- Educational Use: Designed for educational purposes to assist in healthcare decision-making.

---

## 🔧 Features

- **Drug Information**: Get detailed clinical summaries for any drug, tailored for pharmacists and healthcare professionals.
- **Symptom Checker**: Input symptoms and receive AI-generated drug recommendations.
- **Role-based Dashboards**: Separate dashboards for doctors, pharmacists, students, and patients.
- **Structured Codebase**: Fully modular backend and organized frontend for easy contributions.
- **Educational Use**: Designed for educational purposes to assist in healthcare decision-making.

---

## 🗂 Code Structure & Contribution Guide

After the major restructuring, the project now follows a clean, modular structure:

```
.
├── app.py                  # Entry point of the application (registers blueprints)
│
├── backend
│   ├── routes              # All route definitions (Blueprints)
│   │   ├── api_routes.py        # JSON APIs for drug info, symptom checker, etc.
│   │   ├── ai_routes.py         # Gemini / AI endpoints
│   │   ├── auth_routes.py       # Authentication (login, signup)
│   │   ├── dashboard_routes.py  # Dashboards (doctor, pharmacist, etc.)
│   │   ├── feature_routes.py    # Additional features
│   │   ├── error_handlers.py    # 404 / 500 error handlers
│   │   └── __init__.py          # Blueprint registration
│   │
│   ├── utils
│   │   └── gemini_utils.py      # Utility functions for Gemini API
│   │
│   ├── static
│   │   ├── css                  # Stylesheets
│   │   └── js                   # Client-side scripts
│   │
│   └── templates                # Jinja2 HTML templates
│
├── requirements.txt
├── Procfile
├── vercel.json
└── LICENSE
```

### **Where to Add New Features**

- **New API endpoints:**\
  Add a new function in `backend/routes/api_routes.py` (or create a new `*_routes.py` file if it’s a major feature) and register it in `__init__.py`.

- **New AI/Gemini feature:**\
  Use `backend/routes/ai_routes.py` and helper functions from `backend/utils/gemini_utils.py`.

- **New Dashboard Page:**\
  Add a route in `dashboard_routes.py`, create a new HTML file in `backend/templates`, and if needed, CSS/JS in `backend/static`.

- **Error Pages:**\
  Modify or add handlers in `error_handlers.py`.

This modular structure makes it simple to extend the application.

---

## 📚 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Code Structure & Contribution Guide](#code-structure--contribution-guide)
- [Contributing](#contributing)
- [License](#license)
- [Contributors](#️-contributors)


---

## ⛏ Installation

### Prerequisites

1. Python 3.8 or above
2. Flask
3. A valid Google Generative AI API key

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/aditi.git
   cd aditi
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API key:

   - Add your API key as an environment variable named `GEMINI_KEY`.

4. Run the application:

   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## ▶️ Usage

### Endpoints

1. **Home Page**: `GET /`
2. **Drug Information**: `POST /get_drug_info`
   - Input: JSON payload with `drug_name`.
   - Output: JSON response containing clinical drug information.
3. **Symptom Checker**: `POST /symptom_checker`
   - Input: JSON payload with `symptoms`.
   - Output: JSON response with recommended drugs and safety information.

---

## 📊 Logging, Timeout & Retry

- Logs are printed to console and available in deployment logs (e.g., Vercel).
- Gemini API requests use a 10-second timeout with up to 3 retries.
- Events logged: API calls, prompts, errors, exceptions.

---

## 🛠️ Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/aditi.git
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
4. Commit changes:
   ```bash
   git commit -m "Description of your changes"
   ```
5. Push:
   ```bash
   git push origin feature-name
   ```
6. Open a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ❤️ Contributors


## 🙌 A Big Thank You to All Contributors!

[![Contributors](https://contrib.rocks/image?repo=MAVERICK-VF142/Drx.MediMate)](https://github.com/MAVERICK-VF142/Drx.MediMate/graphs/contributors)

<p align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="600">
</p>




## Admin Panel

The admin panel is accessible via /admin-dashboard.html for users with 'admin' role. Features include:

- Managing user accounts: View, edit, delete user profiles.
- Managing records, appointments, prescriptions.
- System notifications and analytics.

### Usage
Sign up with admin role or edit a user to admin in Firestore.

### Testing
Run `python test.py` for unit tests.

