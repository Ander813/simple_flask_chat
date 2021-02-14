from app import create_app
from src.app.views import chat


app = create_app()
app.register_blueprint(chat)


if __name__ == "__main__":
    app.run()
