from flask import Flask, render_template, request, jsonify
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
            status = "success"
        except Exception as e:
            message = f"An error occurred: {e}"
            status = "error"
           # Handle AJAX request: return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': status, 'message': message})
        
        # Fallback for normal (non-AJAX) POST
        return render_template("index.html", message=message)


    # For GET requests
    return render_template("index.html", message=None)

if __name__ == "__main__":
    app.run(debug=True)
