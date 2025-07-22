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

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contributors](#contributors)

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="900">

---

## 📂 Project Structure

The project now follows a modular Flask application structure, enhancing maintainability, scalability, and clarity. Key directories and their responsibilities are:

-   **`app/`**: Contains the core Flask application logic.
    -   `__init__.py`: Initializes the Flask app and registers the main application components.
    -   `config.py`: Manages application-wide settings and environment configurations.
    -   `models.py`: (Currently empty) Reserved for future database model definitions.
    -   **Blueprints (Feature Modules):** Each main feature is organized into its own Blueprint sub-directory:
        -   `drug_info/`: Handles routes and logic for retrieving and displaying drug information using Gemini AI.
        -   `image_processing/`: Manages routes and services for uploading and analyzing medicine images with Gemini Vision AI.
        -   `main/`: Contains general application pages, including the homepage and dashboard routes.
        -   `symptom_checker/`: Manages routes and logic for providing symptom-based drug recommendations via Gemini AI.
    -   `utils/`: Houses reusable helper functions, like API response formatting.
-   **`static/`**: Stores static web assets such as CSS stylesheets and JavaScript files.
-   **`templates/`**: Contains all HTML templates, organized into subdirectories (e.g., `main/`, `drugs/`) that correspond to application features.
-   **`tests/`**: (If applicable) Contains automated tests for the application.
-   **`venv/`**: The Python virtual environment for isolated dependencies.
-   **`.env`**: (Ignored by Git) Used for local environment variables like API keys.
-   **`wsgi.py`**: The main entry point for running the Flask application.
-   `Procfile`, `vercel.json`, `requirements.txt`, `LICENSE`, `README.md`: Other standard project files.

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

