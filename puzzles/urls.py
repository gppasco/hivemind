from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("puzzles/<int:puz_id>", views.render_puz, name="render_puz"),
    path("create", views.create_puzzle, name="create_puzzle"),
    path("about", views.about_page, name="about_page"),

    path("puzzles/letters/<int:puz_id>", views.single_puz, name="single_puz"),
    path("puzzles/new_word", views.new_word, name="new_word"),
    path("puzzles/getwords/<int:puz_id>", views.get_words, name="get_words")

]