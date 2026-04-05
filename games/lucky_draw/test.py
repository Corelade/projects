import unittest
from lucky_draw import *
from unittest.mock import patch


class TestNumericInput(unittest.TestCase):
    @patch("builtins.input", side_effect=["5"])
    def test_in_range_number(self, mock_input):
        "This correctly selects a number in the range and tests it"
        resp = get_numeric_input("Enter a number between 5-9: ")
        self.assertEqual(resp, 5)

    @patch("builtins.input", side_effect=["0", "a", "10", "6"])
    def test_multi_number(self, mock_input):
        "This uses the next number as result if the current number fails"
        resp = get_numeric_input("Enter a number between 5-9: ")
        self.assertEqual(resp, 6)

    @patch("builtins.input", side_effect=[7])
    def test_not_equal_number(self, mock_input):
        "This passes if the input is not equal to output"
        resp = get_numeric_input("Enter a number between 5-9: ")
        self.assertNotEqual(resp, 6)


class TestGame(unittest.TestCase):
    @patch("lucky_draw.get_numeric_input", return_value=1)
    @patch("lucky_draw.random.choice", side_effect=[2, 2])
    @patch("lucky_draw.random.shuffle", side_effect=lambda x: None)
    def test_human_wins(self, _shuffle, _choice, _input):
        winner = game(["AI1", "human"])
        self.assertEqual(winner, "human")
    
    @patch("lucky_draw.get_numeric_input", return_value=1)
    @patch("lucky_draw.random.choice", side_effect=[1, 2])
    @patch("lucky_draw.random.shuffle", side_effect=lambda x: None)
    def test_ai_wins(self, _shuffle, _choice, _input):
        winner = game(["AI1", "human"])
        self.assertEqual(winner, "AI1")


if __name__ == "__main__":
    unittest.main()
