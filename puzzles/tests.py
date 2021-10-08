from django.test import Client, TestCase
from .models import User, Puzzle, Word

# Create your tests here.


# Test creating a puzzle
class PuzzleTestCase(TestCase):

    def setUp(self):

        # Create a user
        sample_user = User.objects.create_user(username="sample",
                                               password="test123",
                                               email="user@email.com")

        # Create a puzzle
        puzzle1 = Puzzle.objects.create(centerLetter="H",
                                        outerLetters="CDEITW")

        # Create words
        word_HIDE = Word.objects.create(text="HIDE", puzzle=puzzle1)
        word_CHEWED = Word.objects.create(text="CHEWED", puzzle=puzzle1)
        word_TWITCHED = Word.objects.create(text="TWITCHED", puzzle=puzzle1)

        for object in Word.objects.all():
            object.guesser.add(sample_user)

    # Testing word scores (+ that the scoring function works properly)
    def test_score_HIDE(self):
        res = Word.objects.get(text="HIDE")
        self.assertEqual(Word.get_score(res), 1)

    def test_score_CHEWED(self):
        res = Word.objects.get(text="CHEWED")
        self.assertEqual(Word.get_score(res), 6)

    def test_score_TWITCHED(self):
        res = Word.objects.get(text="TWITCHED")
        self.assertEqual(Word.get_score(res), 15)

    # Assert that a non-logged-in user is redirected
    def test_puzzles(self):
        c = Client()

        # Access the puzzle page for a normal puzzle
        puz = Puzzle.objects.get(centerLetter="H", outerLetters="CDEITW")

        response = c.get(f"/puzzles/{puz.id}")

        print(response)

        self.assertEqual(response.status_code, 302)

    # Assert that a logged-in user can access a normal puzzle page
    def test_valid_puzzles(self):
        c = Client()
        c.login(username="sample", password="test123")

        # Access the puzzle page for a normal puzzle
        puz = Puzzle.objects.get(centerLetter="H", outerLetters="CDEITW")

        resp = c.get(f"/puzzles/{puz.id}")
        self.assertEqual(resp.status_code, 200)

    # Assert that a logged-in user can't access a non-existing puzzle page
    def test_invalid_puzzles(self):
        c = Client()
        c.login(username="sample", password="test123")

        # Access the puzzle page for a normal puzzle
        puz = Puzzle.objects.get(centerLetter="H", outerLetters="CDEITW")

        resp = c.get(f"/puzzles/{30000}")
        self.assertEqual(resp.status_code, 404)

    # Now check that we can accurately find all words found by a user
    def test_all_words_found(self):
        sample_user = User.objects.get(username="sample")
        puzzle1 = Puzzle.objects.get(centerLetter="H", outerLetters="CDEITW")
        all_words = Word.objects.filter(guesser=sample_user, puzzle=puzzle1)
