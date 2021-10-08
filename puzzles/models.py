from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Puzzle(models.Model):
    # Figure out how to deal with json
    centerLetter = models.CharField(max_length=1)
    outerLetters = models.CharField(max_length=6)

    def serialize(self):
        return {
            "id": self.id,
            "center": self.centerLetter,
            "outer": self.outerLetters,
            "all": self.centerLetter + self.outerLetters
        }

    def __str__(self):
        return f"CENTER: {self.centerLetter}, OUTER: {self.outerLetters}"


class Word(models.Model):
    text = models.CharField(max_length=100)
    guesser = models.ManyToManyField(User, related_name="words")
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE,
                               related_name="words")

    def get_score(self):
        if len(self.text) == 4:
            return 1
        else:
            return len(self.text) + 7 * (len(set(list(self.text))) == 7)

    def serialize(self):
        return {
            "id": self.id,
            "text": text,
            "guesser": guesser,
            "puzzle": puzzle.id
        }

    def __str__(self):
        return f"{self.guesser} guessed {self.text} on puzzle {self.puzzle.id}"
