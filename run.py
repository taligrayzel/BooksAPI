"""Run the Books API."""
from app.main import app
from waitress import serve

if __name__ == "__main__":
    # app.run(debug=True, port=5000)
    serve(app, host="0.0.0.0", port=5000, threads=4)
