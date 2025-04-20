import requests

url = 'http://127.0.0.1:5000/api/invoice'
data = {
    "duedate": "6 June 2025",
    "from_addr": {
        "addr1": "Glasgow, Scotland",
        "addr2": "26 Richmond St, G1 1XH",
        "company_name": "Livingstone Tower"
    },
    "invoice_number": 156,
    "items": [
        {
            "charge": 500.0,
            "title": "Brochure design"
        },
        {
            "charge": 85.0,
            "title": "Hosting (6 months)"
        },
        {
            "charge": 10.0,
            "title": "Domain name (1 year)"
        }
    ],
    "to_addr": {
        "company_name": "Tasker INC.",
        "person_email": "petertasker05@gmail.com",
        "person_name": "Peter Tasker"
    }
}

html = requests.post(url, json=data)
with open('invoice.pdf', 'wb') as f:
    f.write(html.content)
