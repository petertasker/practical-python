from flask import Flask, render_template, request
from datetime import datetime
from weasyprint import HTML
import os

app = Flask(__name__)

@app.route('/api/invoice', methods=['GET', 'POST'])
def generate_invoice():
    if request.method == 'GET':
        return "Send a POST request to generate an invoice", 200

    posted_data = request.get_json()
    if not posted_data:
        return "No data provided", 400

    today = datetime.today().strftime("%d %B %Y")
    duedate = posted_data.get('duedate')
    from_addr = posted_data.get('from_addr')
    to_addr = posted_data.get('to_addr')
    invoice_number = posted_data.get('invoice_number')
    items = posted_data.get('items', [])

    total = sum([i['charge'] for i in items])
    rendered =  render_template('invoice.html',
                           date=today,
                           from_addr=from_addr,
                           to_addr=to_addr,
                           items=items,
                           total=total,
                           invoice_number=invoice_number,
                           duedate=duedate)
    html = HTML(string=rendered)
    rendered_pdf = html.write_pdf()
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "invoice.pdf")
    with open(downloads_path, "wb") as f:
        f.write(rendered_pdf)
    return f"Invoice saved to {downloads_path}", 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)