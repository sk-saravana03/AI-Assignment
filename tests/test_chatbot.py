"""
Automated unit and integration test suite for the College Examination FAQ Chatbot.
Covers:
1. Exact FAQ question matching
2. Paraphrased FAQ question matching
3. Greetings
4. Exit messages
5. Unknown / out-of-domain questions
6. Empty / whitespace inputs
7. Revaluation question
8. Hall ticket question
9. Examination timetable question
10. Results question
11. Flask API endpoints (/api/chat, /api/info)
"""

import unittest
from app import app
from nlp.chatbot import ExamFAQChatbot


class TestExamFAQChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = ExamFAQChatbot(threshold=0.25)
        cls.client = app.test_client()

    # 1. Exact FAQ question
    def test_exact_faq_question(self):
        query = "When are the semester exams?"
        res = self.bot.get_response(query)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["confidence"], 0.25)
        self.assertIn("academic calendar", res["answer"].lower())

    # 2. Paraphrased FAQ questions (multiple forms mapping to same FAQ)
    def test_paraphrased_semester_exam_question(self):
        variations = [
            "Tell me the date of my semester examination",
            "When will semester examinations begin?",
            "What is the semester exam schedule?",
        ]
        for query in variations:
            res = self.bot.get_response(query)
            self.assertEqual(
                res["status"],
                "success",
                f"Failed on variation: {query}",
            )
            self.assertIn("academic calendar", res["answer"].lower())

    # 3. Greeting
    def test_greeting_handling(self):
        greetings = ["hi", "hello", "Hey", "Good morning", "hello!"]
        for g in greetings:
            res = self.bot.get_response(g)
            self.assertEqual(res["status"], "greeting")
            self.assertIn("College Examination FAQ Chatbot", res["answer"])
            self.assertEqual(res["confidence"], 1.0)

    # 4. Exit message
    def test_exit_handling(self):
        exits = ["bye", "exit", "quit", "Goodbye", "bye!"]
        for e in exits:
            res = self.bot.get_response(e)
            self.assertEqual(res["status"], "exit")
            self.assertIn("Best wishes for your examinations", res["answer"])
            self.assertEqual(res["confidence"], 1.0)

    # 5. Unknown / non-examination question
    def test_unknown_question_fallback(self):
        unknown_queries = [
            "What is the capital of Australia?",
            "Can you bake a chocolate cake for me?",
            "Who won the football world cup?",
        ]
        for q in unknown_queries:
            res = self.bot.get_response(q)
            self.assertEqual(res["status"], "below_threshold")
            self.assertIn("couldn't find a relevant answer", res["answer"])
            self.assertLess(res["confidence"], self.bot.threshold)

    # 6. Empty and invalid inputs
    def test_empty_and_short_inputs(self):
        empty_res = self.bot.get_response("")
        self.assertEqual(empty_res["status"], "empty_input")

        space_res = self.bot.get_response("   ")
        self.assertEqual(space_res["status"], "empty_input")

        short_res = self.bot.get_response("?")
        self.assertEqual(short_res["status"], "short_input")

    # 7. Revaluation question
    def test_revaluation_question(self):
        queries = [
            "How do I apply for revaluation?",
            "I want to recheck my exam papers",
            "Revaluation procedure for answer sheets",
        ]
        for q in queries:
            res = self.bot.get_response(q)
            self.assertEqual(res["status"], "success")
            self.assertIn("revaluation", res["answer"].lower())

    # 8. Hall ticket question
    def test_hall_ticket_question(self):
        queries = [
            "How can I download my hall ticket?",
            "Where to get exam admit card?",
            "Steps to download examination entry pass",
        ]
        for q in queries:
            res = self.bot.get_response(q)
            self.assertEqual(res["status"], "success")
            self.assertTrue(
                "hall ticket" in res["answer"].lower()
                or "admit card" in res["answer"].lower()
            )

    # 9. Examination timetable question
    def test_timetable_question(self):
        queries = [
            "Where can I find the examination timetable?",
            "How to get the exam routine schedule?",
            "Exam time table download",
        ]
        for q in queries:
            res = self.bot.get_response(q)
            self.assertEqual(res["status"], "success")
            self.assertIn("timetable", res["answer"].lower())

    # 10. Results question
    def test_results_question(self):
        queries = [
            "When will the semester exam results be published?",
            "Where can I check my examination results?",
            "When are exam marks announced?",
        ]
        for q in queries:
            res = self.bot.get_response(q)
            self.assertEqual(res["status"], "success")
            self.assertIn("results", res["answer"].lower())

    # 11. Flask API: POST /api/chat valid input
    def test_api_chat_valid(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "When are the semester exams?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("answer", data)
        self.assertIn("confidence", data)
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["confidence"], 0.25)

    # 12. Flask API: POST /api/chat greetings
    def test_api_chat_greeting(self):
        response = self.client.post("/api/chat", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "greeting")

    # 13. Flask API: Error handling for invalid JSON payload
    def test_api_chat_invalid_payload(self):
        # Missing JSON body
        res1 = self.client.post("/api/chat", data="not a json", content_type="text/plain")
        self.assertEqual(res1.status_code, 400)

        # Missing message key
        res2 = self.client.post("/api/chat", json={"query": "test"})
        self.assertEqual(res2.status_code, 400)

    # 14. Flask API: GET /api/info
    def test_api_info(self):
        response = self.client.get("/api/info")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["category"], "Examinations")
        self.assertGreaterEqual(data["total_faqs"], 25)
        self.assertEqual(data["threshold"], 0.25)


if __name__ == "__main__":
    unittest.main()
