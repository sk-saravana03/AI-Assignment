"""
Examination FAQ Chatbot Engine.
Demonstrates text preprocessing, TF-IDF vectorization, and cosine similarity matching.
"""

import json
import os
import re
import string
from typing import Any, Dict, List, Optional, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ExamFAQChatbot:
    """College Examination FAQ Chatbot using TF-IDF and Cosine Similarity."""

    # Default similarity threshold for accepting an FAQ match
    DEFAULT_THRESHOLD: float = 0.25

    # Greeting patterns and standard replies
    GREETING_INPUTS = {
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "greetings",
        "namaste",
    }
    GREETING_RESPONSE = (
        "Hello! I am the College Examination FAQ Chatbot. "
        "How can I help you with your examination-related questions today?"
    )

    # Exit keywords and response
    EXIT_INPUTS = {"bye", "exit", "quit", "goodbye", "see you", "close"}
    EXIT_RESPONSE = "Goodbye! Best wishes for your examinations."

    # Fallback message for below-threshold or non-examination queries
    FALLBACK_RESPONSE = (
        "Sorry, I couldn't find a relevant answer to your question. "
        "Please ask an examination-related question or contact the college examination section."
    )

    def __init__(
        self,
        faq_filepath: Optional[str] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        """
        Initialize the NLP Chatbot, loading FAQ knowledge base and fitting TF-IDF model.
        """
        self.threshold = threshold
        self.faq_filepath = faq_filepath or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "faq_data.json",
        )

        # Setup NLTK lemmatizer and stop words with fallbacks
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words("english"))
        except Exception:
            self.stop_words = set()

        # Load knowledge base and compile corpus
        self.faqs: List[Dict[str, Any]] = self._load_faqs()
        self.corpus: List[str] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        if self.faqs:
            self._fit_vectorizer()

    def _load_faqs(self) -> List[Dict[str, Any]]:
        """Load FAQ questions and answers from JSON knowledge base."""
        if not os.path.exists(self.faq_filepath):
            raise FileNotFoundError(f"FAQ data file not found at: {self.faq_filepath}")

        with open(self.faq_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("FAQ data must be a JSON array of items.")
            return data

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess input text:
        1. Lowercase conversion
        2. Unnecessary punctuation & special characters removal
        3. Tokenization (via NLTK word_tokenize with fallback)
        4. Stopword filtering & Lemmatization
        5. Re-assembling into normalized string
        """
        if not text:
            return ""

        # Step 1: Lowercase
        cleaned = text.lower().strip()

        # Step 2: Remove punctuation
        cleaned = re.sub(f"[{re.escape(string.punctuation)}]", " ", cleaned)

        # Step 3: Tokenize
        try:
            tokens = word_tokenize(cleaned)
        except Exception:
            tokens = cleaned.split()

        # Step 4: Lemmatize & filter non-alpha tokens
        processed_tokens = []
        for token in tokens:
            if token.isalnum():
                lemma = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemma)

        return " ".join(processed_tokens)

    def _build_faq_document(self, faq_item: Dict[str, Any]) -> str:
        """
        Construct a rich searchable representation for each FAQ by combining
        the canonical question, keywords, and category.
        """
        question = faq_item.get("question", "")
        keywords = " ".join(faq_item.get("keywords", []))
        category = faq_item.get("category", "")
        combined = f"{question} {keywords} {category}"
        return self.preprocess_text(combined)

    def _fit_vectorizer(self) -> None:
        """Fit the TF-IDF Vectorizer on all FAQ documents and build the matrix."""
        self.corpus = [self._build_faq_document(item) for item in self.faqs]

        # Use 1-gram and 2-gram combinations for richer semantic representation
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            norm="l2",
            sublinear_tf=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def is_greeting(self, message: str) -> bool:
        """Check whether the user input is a greeting."""
        cleaned = message.lower().strip()
        cleaned_no_punct = re.sub(f"[{re.escape(string.punctuation)}]", "", cleaned)
        return cleaned in self.GREETING_INPUTS or cleaned_no_punct in self.GREETING_INPUTS

    def is_exit(self, message: str) -> bool:
        """Check whether the user input is an exit or farewell."""
        cleaned = message.lower().strip()
        cleaned_no_punct = re.sub(f"[{re.escape(string.punctuation)}]", "", cleaned)
        return cleaned in self.EXIT_INPUTS or cleaned_no_punct in self.EXIT_INPUTS

    def find_best_faq(self, query: str) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Transform query into TF-IDF vector, compute Cosine Similarity against FAQ matrix,
        and return the best matching FAQ item and its similarity score.
        """
        if not self.vectorizer or self.tfidf_matrix is None or not self.faqs:
            return None, 0.0

        processed_query = self.preprocess_text(query)
        if not processed_query.strip():
            return None, 0.0

        query_vec = self.vectorizer.transform([processed_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        best_index = int(similarities.argmax())
        best_score = float(similarities[best_index])

        return self.faqs[best_index], round(best_score, 4)

    def get_response(self, user_message: Optional[str]) -> Dict[str, Any]:
        """
        Main entry point for generating response:
        - Validates input
        - Handles Greetings & Exit
        - Runs TF-IDF & Cosine Similarity matching
        - Applies similarity threshold check
        - Returns structured answer dictionary
        """
        # Step 1: Validate input
        if user_message is None or not user_message.strip():
            return {
                "answer": "Please enter a valid examination question.",
                "confidence": 0.0,
                "status": "empty_input",
                "matched_faq": None,
            }

        stripped_message = user_message.strip()

        # Step 2: Handle Greetings
        if self.is_greeting(stripped_message):
            return {
                "answer": self.GREETING_RESPONSE,
                "confidence": 1.0,
                "status": "greeting",
                "matched_faq": None,
            }

        # Step 3: Handle Exit
        if self.is_exit(stripped_message):
            return {
                "answer": self.EXIT_RESPONSE,
                "confidence": 1.0,
                "status": "exit",
                "matched_faq": None,
            }

        # Step 4: Handle very short or symbol-only inputs
        if len(stripped_message) < 2 or not any(c.isalnum() for c in stripped_message):
            return {
                "answer": "Your input seems too brief. Please type a specific question about exams, hall tickets, results, or timetables.",
                "confidence": 0.0,
                "status": "short_input",
                "matched_faq": None,
            }

        # Step 5: Match with Knowledge Base using TF-IDF & Cosine Similarity
        matched_faq, score = self.find_best_faq(stripped_message)

        # Step 6: Similarity Threshold Check
        if matched_faq and score >= self.threshold:
            return {
                "answer": matched_faq["answer"],
                "confidence": score,
                "status": "success",
                "matched_faq": {
                    "id": matched_faq.get("id"),
                    "question": matched_faq.get("question"),
                    "category": matched_faq.get("category"),
                },
            }

        # Step 7: Fallback message if confidence is below threshold
        return {
            "answer": self.FALLBACK_RESPONSE,
            "confidence": score,
            "status": "below_threshold",
            "matched_faq": None,
        }
