# JobFit AI

JobFit AI is an AI-powered application that helps job seekers evaluate and improve their resumes for specific job postings.  
The app analyzes a CV and a job description, identifies relevant skills, computes a match score, and suggests improvements such as missing keywords or tailored bullet points.  

This project is being developed as a **portfolio project** to demonstrate skills in Python, NLP, web development, and deployment.

---

## 🚀 Features (MVP)
- Upload CV (PDF/DOCX) and paste job description
- Clean text processing with spaCy
- Keyword extraction using YAKE/RAKE
- Semantic similarity with Sentence-Transformers (MiniLM, free local model)
- Match score (0–100) based on coverage + embeddings similarity
- Present vs. missing keyword highlights
- Section health detection (Experience, Skills, Projects)
- Copy-ready bullet suggestions (template-based)

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI (later phases)
- **Frontend:** Streamlit (MVP) → Next.js + Tailwind CSS (full build)
- **NLP:** spaCy, Sentence-Transformers, YAKE
- **Data Handling:** pdfminer.six, python-docx
- **Deployment (free tier):** Vercel, Render, Neon/Postgres

---

## 📂 Project Structure (planned)

## 📂 Project Structure

```bash
jobfit-ai/
│
├── app/                         # Main application package
│   ├── pipeline/                 # NLP + scoring logic
│   │   ├── __init__.py
│   │   ├── text_cleaner.py       # text normalization, tokenization, stopword removal
│   │   ├── keyword_extractor.py  # YAKE/RAKE keyword extraction
│   │   ├── scorer.py             # match score calculation
│   │
│   └── ui/                       # Frontend code
│       ├── __init__.py
│       └── main_app.py           # Streamlit MVP entry point
│
├── data/                         # Input examples (not production data)
│   ├── sample_resume.pdf
│   └── sample_job.txt
│
├── notebooks/                    # Prototyping & experiments
│   └── text_cleaning_demo.ipynb
│
├── tests/                        # Unit tests (pytest/unittest)
│   └── test_pipeline.py
│
├── .gitignore                    # Ignore cache, venv, logs, etc.
├── LICENSE                       # License file (MIT)
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
└── setup.cfg / pyproject.toml    # (Optional) Config for linting/packaging

```



---

## 🎯 Roadmap
- **Week 1–2:** Streamlit MVP (upload, keyword extraction, match score)
- **Week 3–4:** Explanations, bullet suggestions, export report
- **Week 5–6:** Split into FastAPI backend + Next.js frontend
- **Week 7–8:** Auth, history, deployment, demo video

---

## 📸 Demo (coming soon)
Screenshots and a demo video link will be added after MVP is deployed.

---

## 🤝 Contributing
This is a personal learning project. Suggestions, issues, and improvements are welcome.

---

## 📜 License
MIT License – free to use, modify, and share.
