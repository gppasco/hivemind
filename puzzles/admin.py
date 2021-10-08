from django.contrib import admin
from .models import User, Puzzle, Word

# Register your models here.
admin.site.register(User)
admin.site.register(Puzzle)
admin.site.register(Word)
