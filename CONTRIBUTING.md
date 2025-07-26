# Contributing Guidelines

Thank you for considering contributing to **Aditi – Your Pharmaceutical Assistant (Drx.MediMate)**!  
We welcome contributions that help improve features, fix bugs, add documentation, or enhance the user experience.

---

## 🛠 How to Contribute

### 1. Fork the repository
Click the **Fork** button on the top-right of the repository page on GitHub.

### 2. Clone your fork
Clone your forked repository to your local machine:

```bash
git clone https://github.com/<your-username>/Drx.MediMate.git
cd Drx.MediMate
```

### 3. Add the upstream (only once)
To stay up to date with the original repository:

```bash
git remote add upstream https://github.com/MAVERICK-VF142/Drx.MediMate.git
```

### 4. Create a new branch
Always create a branch for your changes:

```bash
git checkout -b feature-name
```

### 5. Make your changes
Follow the **code structure**:

- Add new routes in `backend/routes/`
- Place utility/helper code in `backend/utils/`
- Add templates in `backend/templates/`
- Add static assets (CSS/JS) in `backend/static/`

Test your changes locally:

```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

### 6. Commit your changes
Write a meaningful commit message:

```bash
git add .
git commit -m "Add: description of your changes"
```

### 7. Keep your fork updated
Before pushing, fetch and rebase with upstream:

```bash
git fetch upstream
git rebase upstream/main
```

Resolve any conflicts if prompted.

### 8. Push and open a Pull Request
Push your branch:

```bash
git push origin feature-name
```

Then open a Pull Request from your fork to the main repository.

---

## 💡 Tips for Contributions

- Make small, focused pull requests.
- Write clear commit messages.
- Ensure your code runs without errors locally.
- Update the documentation (README/CONTRIBUTING) if required.

---

## 📜 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🤝 Need Help?

If you face any difficulty while contributing, feel free to open an issue or reach out to the maintainers.

---

Happy Coding! 🎉
