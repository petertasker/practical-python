# Practical Python Projects

## 🕹️ Project 1: Steam Scraper

This project scrapes Steam's [New Releases page](https://store.steampowered.com/explore/new/) and outputs the results as structured JSON. It uses XMLX for parsing and supports both local execution and a simple web API via GET requests.

Each game entry includes:
- **Title**
- **Original Price**
- **Discount Price**
- **Discount Percentage**
- **Tags**
- **Platforms**

### 📦 Dependencies
```bash
pip install -r .\steam-scraper\requirements.txt
```

### ▶️ Running Locally
To run the scraper locally:

```bash
py .\steam-scraper\scraper.py
```

### 🌐 Running as a Server
To start the web API:

```bash
py .\steam-scraper\scraper.py server
```

The server will listen at:
```
http://localhost:5000/api/steam/new_releases
```

### ⚙️ Request Parameters
You can include any combination of the following query parameters:

| Parameter    | Description                        | Example              |
|--------------|------------------------------------|----------------------|
| discount_only| Only show discounted games         | discount_only=true   |
| platform     | Filter by platform (Windows, MacOS, linux) | platform=linux      |
| tag          | Filter by tag (e.g., "Strategy")   | tag=Strategy         |

#### Example Request:

```
http://localhost:5000/api/steam/new_releases?tag=Strategy&platform=linux&discount_only=true
```

#### Sample Response:

```json
[
  {
    "title": "Minutescape",
    "original_price": "4.99",
    "final_price": "4.49",
    "discount_pct": "-10%",
    "tags": ["Strategy", "Idler", "Clicker", "Bullet Hell"],
    "platforms": ["Windows", "MacOS", "linux"]
  }
]
```

---

## 🧾 Project 2: Web-Based Invoice Generator

This project creates a downloadable PDF invoice from structured data sent via a POST request.

### 📦 Dependencies

```bash
pip install -r .\invoice-generator\requirements.txt
```

### ▶️ Starting the Server

```bash
py .\invoice-generator\app.py
```

The server listens at:
```
http://127.0.0.1:5000/api/invoice
```

### 📤 Sending a Request  
You can test the API using the included example in [app_test.py](https://github.com/petertasker/practical-python/blob/master/invoice-generator/app_test.py).  
Once the request is processed, a PDF invoice is generated and saved to your Downloads folder.

---

## 📱 Project 3: League of Legends Esports SMS Bot

This app will send you an SMS message of the next scheduled League of Legends esports game. You are able to specify which region you are after.

### 📦 Dependencies
```bash
pip install -r .\sms-next-lol-game\requirements.txt
```

For this, I used the [ClickSend](https://dashboard.clicksend.com/) SMS API to send messages. 

You will either need to register with them and replace your credentials at the top of [app.py](https://github.com/petertasker/practical-python/tree/master/sms-next-lol-game/app.py), or find another SMSing API.

```python
CLICKSEND_USERNAME = "your_username"
CLICKSEND_API_KEY = "your_api_key"
```

### ▶️ Starting the Server

```bash
py .\sms-next-lol-game\app.py
```

The server listens at:
```
http://127.0.0.1:5000/
```

Example JSON request:
```json
{
    "From": "your number here",
    "Body": "LPL"
}
```
The `Body` element is optional, but it can be used to specify which league you want.

You can use [send_sms.py](https://github.com/petertasker/practical-python/tree/master/sms-next-lol-game/app.py) to send a `POST` request for you, but you'll need to provide a number.

---


## 📰 Project 4: Article Summariser and Image generator

This project takes a news article URL, generates a summarised version using a transformer model, and overlays that summary text onto cropped versions of the article's header image, formatted for vertical screens (1080x1920). It uses `newspaper3k` for scraping, Hugging Face Transformers for summarisation, and wand for image editing. Output images are saved with captions near the top and bottom, ready for mobile viewing or sharing.

### 🐍 Running the program
```bash
py .\article-story-generator\news_summary.py <article>
```

You will then find the output of your program in `.\article-summariser\output`  


---


## 🌎 Project 5: History Location Visualiser

This app will turn your browser history (or any file of domains) into an interactive map tool which shows the server locations that you are pinging to.

### 📦 Dependencies
```bash
pip install -r .\server-visualiser\requirements.txt
```

### Setup

You will need to export your history from your browser into a text file. 
* In Firefox, this can be done by going to `History` -> `Manage History` -> Selecting a time period, and then copy and pasting into a file
* On chromium, you can try [https://chromewebstore.google.com/detail/dihloblpkeiddiaojbagoecedbfpifdj?utm_source=item-share-cb](this extension) to export your history.

You need to save your file as `history-data.txt` and place it in `\practical-python\server-visualiser\`.

After running the script, a `HTML` file will be generated which is your interactive map  

🚧 *More Projects Coming Soon!* 🚧  
Most projects (and the repo title) are inspired by [practicalpython.yasoob.me](https://practicalpython.yasoob.me)
