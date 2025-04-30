from flask import Flask, render_template, request
from scrapper import extract_multiple_contacts
from db_setup import connect_to_db

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        url = request.form["url"]
        tags = request.form["tags"].split(",")
        try:
            conn = connect_to_db()
            extract_multiple_contacts(url, tags, conn)
            conn.commit()
            conn.close()
            message = "Data extracted and saved successfully!"
        except Exception as e:
            message = f"An error occurred: {e}"
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
