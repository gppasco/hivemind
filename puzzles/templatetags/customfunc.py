from django import template
from ..models import User, Puzzle, Word

register = template.Library()


# Helper function to return the score the current user has on a given puzzle
@register.simple_tag
def score(user, puz_id):

    print("This custom function is working!")
    found_puzzle = Puzzle.objects.get(pk=puz_id)

    # Find all the words
    found_words = Word.objects.filter(guesser=user, puzzle=found_puzzle)

    total_score = 0

    for word in found_words:
        total_score += Word.get_score(word)

    return total_score
