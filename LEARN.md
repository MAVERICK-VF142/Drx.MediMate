# Learn Drx.MediMate

Welcome to **Drx.MediMate** (also known as **Aditi**)! This guide will help you get started with using and understanding the project.

## What is Drx.MediMate?

Drx.MediMate (Aditi) is an AI-powered pharmaceutical assistant built with Flask. It provides clinical drug information, symptom-based drug recommendations, and serves as an educational tool for healthcare professionals. The application leverages Google's Generative AI (Gemini Model) to deliver accurate and helpful pharmaceutical guidance.

## Key Features

- **Drug Information**: Get detailed clinical summaries for any drug, tailored for pharmacists and healthcare professionals
- **Symptom Checker**: Input symptoms and receive AI-generated drug recommendations following evidence-based guidelines
- **Educational Use**: Designed for educational purposes to assist in healthcare decision-making
- **User-friendly interfaces** for healthcare providers and patients
- **Integration capabilities** with AI-powered responses

## Getting Started

### 1. Prerequisites

- [Python 3.8 or above](https://www.python.org/downloads/)
- Flask framework
- A valid Google Generative AI API key
- Git for version control

### 2. Clone the Repository

```bash
git clone https://github.com/MAVERICK-VF142/Drx.MediMate.git
cd Drx.MediMate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Environment

Set up your API key as an environment variable named `GEMINI_KEY`:

```bash
export GEMINI_KEY=your_api_key_here
```

### 5. Run the Application

```bash
python app.py
```

### 6. Access the Application

Open your browser and navigate to `http://127.0.0.1:5000/` to start using the application.

### 7. Explore the Code

- The main application logic is in `app.py`
- Frontend templates are in the `/templates` directory
- Static assets (CSS, JS, images) are in the `/static` directory
- Configuration and dependencies are managed through `requirements.txt`

## API Endpoints

- **Home Page**: `GET /` - Displays the main landing page
- **Drug Information**: `POST /get_drug_info` - Get clinical drug information
- **Symptom Checker**: `POST /symptom_checker` - Get drug recommendations based on symptoms

## Documentation

- Review the code comments and inline documentation for insights
- Check the [README.md](./README.md) for detailed setup and usage instructions
- Explore the Flask templates to understand the user interface

## Where to Get Help

- For common questions, check the [Issues](https://github.com/MAVERICK-VF142/Drx.MediMate/issues) page
- For direct questions, open a new issue describing your problem or suggestion
- Review the existing documentation in README.md for additional guidance

## Contributing

Interested in contributing? See [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

---

Happy coding and learning with Drx.MediMate!