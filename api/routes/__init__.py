"""HTTP route registration."""


def register_routes(app):
    from routes import pages, quiz, translate

    pages.register(app)
    quiz.register(app)
    translate.register(app)
