import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django import forms

from .models import User, Puzzle, Word


class PuzzleForm(forms.Form):
    center_letter = forms.CharField(label="Necessary letter")
    outer_letters = forms.CharField(label="Outer letters")


def index(request):
    all_puz = Puzzle.objects.all()
    return render(request, "puzzles/index.html", {
        "puzzles": all_puz
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "puzzles/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "puzzles/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "puzzles/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "puzzles/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "puzzles/register.html")


def about_page(request):
    return render(request, "puzzles/instructions.html")


# Render a single puzzle
@login_required(login_url="login")
def render_puz(request, puz_id):
    try:
        puzzle = Puzzle.objects.get(pk=puz_id)
    except Puzzle.DoesNotExist:
        raise Http404("Puzzle not found.")

    return render(request, "puzzles/puzzle.html", {
        "center": puzzle.centerLetter,
        "outer": list(puzzle.outerLetters),
        "id": puzzle.id,
    })


# Fetch a single puzzle's letters (useful for API calls)
def single_puz(request, puz_id):
    try:
        puzzle = Puzzle.objects.get(pk=puz_id)
    except Puzzle.DoesNotExist:
        return JsonResponse({"error": "Puzzle not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(puzzle.serialize())

    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)


# Create a puzzle
@login_required(login_url="login")
def create_puzzle(request):
    if request.method == "POST":
        form = PuzzleForm(request.POST)
        if form.is_valid():
            inner = form.cleaned_data["center_letter"].upper()
            outer = form.cleaned_data["outer_letters"].upper()

            # Return an error message if the form is invalid
            if len(inner) != 1:
                messages.info(request, "Necessary Letter must be one letter")
                return render(request, "puzzles/create.html", {
                                "form": form
                            })
            elif len(outer) != 6:
                messages.info(request, "Outer Letters must be six letters")
                return render(request, "puzzles/create.html", {
                                "form": form
                            })
            elif len(set(inner+outer)) != 7:
                messages.info(request, "All letters must be unique")
                return render(request, "puzzles/create.html", {
                                "form": form
                            })
            else:
                # Create a new puzzle
                new_puzzle = Puzzle.objects.create(centerLetter=inner,
                                                   outerLetters=outer)
                new_puzzle.save()
                return HttpResponseRedirect(reverse("render_puz",
                                                    args=[new_puzzle.id]))
        else:
            return render(request, "puzzles/create.html", {
                "form": form
            })
    else:
        return render(request, "puzzles/create.html", {
                        "form": PuzzleForm()
                    })


# Return the list of words for a given user and puzzle
def get_words(request, puz_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)

    try:
        found_puzzle = Puzzle.objects.get(pk=puz_id)
    except Puzzle.DoesNotExist:
        return JsonResponse({"error": "Puzzle not found."}, status=404)

    # Get all words for that puzzle and user
    found_words = Word.objects.filter(guesser=request.user,
                                      puzzle=found_puzzle)

    # Serialize that bad boy
    json_data = serializers.serialize("json", found_words)

    return JsonResponse(json_data, safe=False)


# Create a new word object
@csrf_exempt
def new_word(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)

    guess = data['word']
    puz_id = data['puzId']

    try:
        found_puz = Puzzle.objects.get(pk=puz_id)
    except Puzzle.DoesNotExist:
        return JsonResponse({"error": "Puzzle not found."}, status=404)

    word = Word.objects.create(text=guess, puzzle=found_puz)

    word.guesser.add(request.user)
    word.save()

    return JsonResponse({"message": "Word created successfully."}, status=201)
