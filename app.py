from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from scrapper import extract_multiple_contacts
from db_setup import connect_to_db
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        url = request.form["url"]
        block_selector = request.form.get("block_selector")
        
        try:
            conn = connect_to_db()
            extract_multiple_contacts(url, conn, block_selector)
            conn.commit()
            conn.close()
            message = "Data extracted and saved successfully!"
            status = "success"
        except Exception as e:
            message = f"An error occurred: {e}"
            status = "error"
           # Handle AJAX request: return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': status, 'message': message, 'redirect_url': url_for('results')})
        
        
            # Standard form submission
            return redirect(url_for('results'))

        return render_template("index.html", message=None)

        
        # # Fallback for normal (non-AJAX) POST
        # return render_template("index.html", message=message)


    # For GET requests
    return render_template("index.html", message=None)

@app.route("/results", methods=["GET"])
def results():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id,company_url FROM distributors_contacts group by company_url ORDER BY id DESC")
    urls = cursor.fetchall()
    conn.close()
    return render_template("results.html", urls=urls)


@app.route("/export_csv", methods=["POST"])
def export_csv():
    url = request.form["url"]
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM distributors_contacts WHERE company_url = %s", (url,))
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    
    conn.close()

    def generate():
        yield ','.join(headers) + '\n'
        for row in rows:
            yield ','.join(str(item) for item in row) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": f"attachment; filename=export_{url.replace('/', '_')}.csv"})




if __name__ == "__main__":
    app.run(debug=True)
