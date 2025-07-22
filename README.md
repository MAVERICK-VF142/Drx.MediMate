# 🦖 Aditi - Your Pharmaceutical Assistant

<p align="center">
  <img src="https://github.com/user-attachments/assets/ad6c0817-c112-4936-86a9-578190e5fd89" alt="welcome-gif-24" width="300" />
</p>

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="900">

## 📈 Project Overview
**Aditi** is a Flask-based web application that serves as your AI-powered pharmaceutical assistant. It provides:
- Clinical drug information, including therapeutic uses, dosage guidelines, side effects, contraindications, and drug interactions.
- Symptom-based drug recommendations following evidence-based guidelines.
- Educational Use: Designed for educational purposes to assist in healthcare decision-making.

---

## 🔧 Features

- **Drug Information**: Get detailed clinical summaries for any drug, tailored for pharmacists and healthcare professionals.
- **Symptom Checker**: Input symptoms and receive AI-generated drug recommendations.
- **Educational Use**: Designed for educational purposes to assist in healthcare decision-making.

---

## 🔍 Technology Stack
- **Backend**: Python, Flask
- **AI**: Google Generative AI (Gemini Model)
- **Frontend**: HTML, CSS (Flask templates)
- **Hosting**: Vercel

---

## 📚 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contributors](#contributors)

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="900">

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
   - Displays the main landing page.

2. **Drug Information**: `POST /get_drug_info`
   - Input: JSON payload with `drug_name`.
   - Output: JSON response containing clinical drug information.

3. **Symptom Checker**: `POST /symptom_checker`
   - Input: JSON payload with `symptoms`.
   - Output: JSON response with recommended drugs and safety information.

---

## 📊 Logging, Timeout & Retry

Aditi now includes robust observability features to improve reliability and debugging:

### ✅ Logging

- All API calls, AI prompts/responses, errors, and exceptions are logged.
- Logs are saved to both the console and a file.

📍 **Log File Location:** `logs/app.log`

> 💡 Create the `logs/` directory manually before running the app:
```bash
mkdir logs
```

### ✅ Timeout

- All Gemini API calls are limited to 10 seconds maximum.
- If Gemini does not respond in this time, the request is retried.

### ✅ Retry Logic

- Failed or timed-out Gemini API calls are retried up to **3 times**.
- **Exponential backoff is used**: delays of `2s`, `4s`, and `8s` between retries.

This helps prevent app freezes due to slow network or external API issues.

---

## 🛠️ Contributing

Contributions are welcome! Follow these steps to contribute:
1. Fork the repository:
   ```bash
   git fork https://github.com/your-username/aditi.git
   ```

2. Clone your forked repository:
   ```bash
   git clone https://github.com/your-username/aditi.git
   ```

3. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```

4. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```

5. Push your branch:
   ```bash
   git push origin feature-name
   ```

6. Open a pull request to the main repository.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ❤️ Contributors

A big thank you to all contributors!

[![Contributors](https://contrib.rocks/image?repo=MAVERICK-VF142/Drx.MediMate)](https://github.com/MAVERICK-VF142/Drx.MediMate/graphs/contributors)

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="900">

