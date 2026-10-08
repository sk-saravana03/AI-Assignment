# College Examination FAQ Chatbot Using Natural Language Processing

A practical Natural Language Processing (NLP) web application built for college practical assignments to assist students with examination-related queries.

---

## 1. Project Overview

- **Course Assignment:** "Develop a College FAQ Chatbot to answer frequently asked questions."
- **Selected Category:** **Examinations**
- **Project Title:** *College Examination FAQ Chatbot Using Natural Language Processing*
- **Architecture:** Local Flask Backend + NLP Information Retrieval Pipeline + Responsive Web Interface

This application uses classical, academically grounded Natural Language Processing techniques: **Text Preprocessing, TF-IDF Vectorization, and Cosine Similarity** to match student questions in natural language against an authoritative knowledge base of college examination FAQs.

---

## 2. Key Features

1. **Natural Language Understanding:** Recognizes varied phrasing and synonyms (e.g., *"When are semester exams?"*, *"When will semester examinations begin?"*, *"What is the semester exam date?"*).
2. **Realistic FAQ Knowledge Base:** Includes 28 curated FAQs covering hall tickets, schedules, fees, attendance criteria, backlogs, supplementary exams, grading, malpractice rules, and revaluation.
3. **Conversational Courtesy:** Detects user greetings (`hi`, `hello`, `good morning`) and exit messages (`bye`, `quit`, `exit`).
4. **Confidence Thresholding:** Configurable similarity threshold (`THRESHOLD = 0.25`) to trigger graceful fallback when questions fall outside examination topics or are insufficiently similar.
5. **Interactive UI:** Student-friendly responsive interface with quick-suggestion chips, chat clearing, match confidence scores, and typing indicators.
6. **No External Paid APIs:** Operates 100% locally without OpenAI, Gemini API, or external cloud services.

---

## 3. Technology Stack

- **Language:** Python 3 (Tested on 3.14 / 3.10+)
- **NLP Library:** [NLTK](https://www.nltk.org/) (Tokenization, Stopwords, WordNet Lemmatization)
- **Vectorization & Similarity:** [scikit-learn](https://scikit-learn.org/) (`TfidfVectorizer`, `cosine_similarity`)
- **Backend Framework:** [Flask](https://flask.palletsprojects.com/)
- **Frontend:** HTML5, Vanilla CSS3 (Custom responsive academic design), Modern JavaScript (Fetch API)

---

## 4. NLP Methodology

The core matching architecture follows an Information Retrieval (IR) pipeline:

```
User Query
   ↓
[Text Preprocessing]
  • Lowercasing
  • Punctuation removal
  • Tokenization (NLTK word_tokenize)
  • Lemmatization (NLTK WordNetLemmatizer)
  • Stopwords elimination
   ↓
[TF-IDF Vectorization]
  • scikit-learn TfidfVectorizer (unigrams + bigrams, sublinear TF)
  • Transforms query into sparse TF-IDF feature vector
   ↓
[Cosine Similarity Calculation]
  • Measures angle/similarity between query vector & FAQ documents
   ↓
[Best Match Selection & Threshold Verification]
  • Score ≥ 0.25  →  Return verified FAQ Answer + Confidence
  • Score < 0.25  →  Return Graceful Fallback Message
```

---

## 5. Project Directory Structure

```
AI assignment/
│
├── app.py                      # Flask web application & REST API routes
├── requirements.txt            # Python dependencies
├── README.md                   # Complete academic documentation
│
├── data/
│   └── faq_data.json           # 28 Structured examination FAQ entries
│
├── nlp/
│   ├── __init__.py             # Module initialization
│   └── chatbot.py              # Text preprocessing, TF-IDF, and Cosine engine
│
├── templates/
│   └── index.html              # Chatbot web interface template
│
├── static/
│   ├── css/
│   │   └── style.css           # Styling and responsive layouts
│   └── js/
│       └── script.js           # Client-side chat logic & async fetch
│
└── tests/
    └── test_chatbot.py         # 14 automated unit and integration tests
```

---

## 6. Installation & Setup

### Step 1: Clone or Open the Workspace
Navigate to the project root directory:
```bash
cd "AI assignment"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download NLTK Corpora (One-time setup)
Run the following Python one-liner to ensure tokenizer, lemmatizer, and stopword corpora are downloaded:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet')"
```

---

## 7. How to Run

Start the Flask server:
```bash
python app.py
```

Then open your browser and visit:
```
http://127.0.0.1:5000/
```

---

## 8. REST API Specification

### Chat Endpoint
- **URL:** `POST /api/chat`
- **Headers:** `Content-Type: application/json`

**Sample Request:**
```json
{
  "message": "When are the semester exams?"
}
```

**Sample Response:**
```json
{
  "answer": "The semester examination dates are published in the official academic calendar. Students can also check the student portal for the finalized examination schedule.",
  "confidence": 0.584,
  "status": "success"
}
```

---

## 9. Automated Testing

Run the full automated test suite using Python's standard `unittest`:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Verified Test Cases:
1. Exact FAQ questions
2. Paraphrased FAQ questions (multiple forms mapping to same FAQ)
3. Greetings handling (`hi`, `hello`, `good morning`)
4. Exit handling (`bye`, `quit`, `exit`)
5. Unknown / non-examination questions (fallback triggering)
6. Empty and short inputs
7. Revaluation questions
8. Hall ticket questions
9. Examination timetable questions
10. Results publication questions
11. Flask API endpoints and error responses

---

## 10. Expected Behavior

- **Accurate Information Retrieval:** Questions addressing examination schedules, hall ticket printing, fees, and results receive precise, institution-neutral answers.
- **Graceful Fallback:** Queries unrelated to college examinations (e.g., general trivia, off-topic requests) yield a polite notice guiding students to contact the examination cell.
- **Robustness:** Handles uppercase, mixed casing, extra punctuation, and excessive whitespace without crashing.

---

## 11. Limitations & Future Enhancements

### Limitations
- **Corpus-Bound Knowledge:** Relies on the pre-defined 28-question FAQ knowledge base; questions completely outside this domain receive the fallback response.
- **Static Matching:** Operates using classical lexical and semantic n-gram TF-IDF rather than deep contextual transformers or neural generative models.

### Future Enhancements
- Integration with student information systems (SIS) for personalized attendance and grade lookups.
- Multi-lingual examination query support for regional languages.
- Voice-based query input and speech synthesis for accessibility.

