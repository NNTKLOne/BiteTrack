import unittest
from LLM import LlamaApp

class TestLlamaApp(unittest.TestCase):

    def setUp(self):
        self.app = LlamaApp()

    def test_call_llama_api(self):
        query = "valgiau kebabą su česnakiniu padažu"
        response = self.app.call_llama_api(query)

        self.assertIsInstance(response, dict)

        if "text" in response:
            # ar geras formatas
            self.assertIn("- Patiekalas:", response["text"])
        elif "error" in response:
            self.assertIn("Klaida", response["error"])

    def test_process_response_valid(self):
        response = {
            "text": "- Patiekalas: Koldūnai su sviestu\n- Patiekalas: Kepsnys su bulvėmis"
        }
        self.app.process_response(response)

        self.assertIn("Aptikti patiekalai:", self.app.output_label.text)
        self.assertIn("- Patiekalas: Koldūnai su sviestu", self.app.output_label.text)
        self.assertIn("- Patiekalas: Kepsnys su bulvėmis", self.app.output_label.text)

    def test_process_response_error(self):
        response = {"error": "API klaida"}
        self.app.process_response(response)

        self.assertEqual(self.app.output_label.text, "API klaida")

    def test_empty_input(self):
        """kai tuscias inputas"""
        self.app.input_box.text = ""
        self.app.send_query(None)

        self.assertEqual(self.app.output_label.text, "Prašome įvesti tinkamą patiekalą.")

    def test_no_dishes_in_query(self):
        """kai nera patiekalu query"""
        query = "Šiandien žiūrėjau filmą ir klausiau muzikos"
        response = self.app.call_llama_api(query)

        self.assertIsInstance(response, dict)
        if "text" in response:
            self.assertNotIn("- Patiekalas:", response["text"])

    def test_multiple_dishes_in_query(self):
        """testas keliems patiekalams query"""
        query = "valgiau koldūnus su grietine ir kepsnys su bulvėmis"
        response = self.app.call_llama_api(query)

        self.assertIsInstance(response, dict)

        if "text" in response:
            self.assertIn("- Patiekalas:", response["text"])
            self.assertIn("Koldūnai su grietine", response["text"])
            self.assertIn("Kepsnys su bulvėmis", response["text"])

    def test_invalid_api_response_format(self):
        """Netinkamam API texto formatui"""
        response = {"unexpected_key": "something_wrong"}
        self.app.process_response(response)

        self.assertEqual(self.app.output_label.text, "Negauta atsakymo")


if __name__ == "__main__":
    unittest.main()
