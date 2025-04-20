import json
import requests
import lxml.html
import regex
from flask import Flask, jsonify, request

app = Flask(__name__)

class Game():
    def __init__(self, title, original_price, final_price, discount_pct, tags, platforms):
        self.title = title
        self.original_price = original_price
        self.final_price = final_price
        self.discount_pct = discount_pct
        self.tags = tags
        self.platforms = platforms

    def __getitem__(self, key):
        return getattr(self, key)

def scrape_games():
    html = requests.get('https://store.steampowered.com/explore/new/')
    doc = lxml.html.fromstring(html.content)

    # Return a list of all <div>s in the page which have an id of tab_newreleases_content
    # We can take out the first element of the list which would be <div>.
    # "//" acts as a recursive filter, much like ** in git
    # div selects all <div> tags.
    # @id pattern matches for the given id.

    new_releases = doc.xpath('//div[@id="tab_newreleases_content"]')[0]


    # "." asks for all children of the new_releases content
    # @class pattern matches for the class
    # text() unwraps the elements into text form

    game_items = new_releases.xpath('.//a[contains(@class, "tab_item")]')
    games = []

    # Process each game individually
    for item in game_items:
        # Extract title
        title = item.xpath('.//div[@class="tab_item_name"]/text()')[0]

        # Extract tags
        tags_text = item.xpath('.//div[@class="tab_item_top_tags"]')[0].text_content()
        tags = tags_text.split(', ')

        # Extract platforms
        platform_spans = item.xpath('.//span[contains(@class, "platform_img")]')
        platforms = [t.get('class').split(' ')[-1].replace("win", "Windows").replace("mac", "MacOS") for t in
                     platform_spans]
        if 'hmd_separator' in platforms:
            platforms.remove('hmd_separator')

        # Price handling - check if the game has a discount
        discount_div = item.xpath('.//div[contains(@class, "discount_block")]')

        if discount_div and len(discount_div[0].xpath('.//div[@class="discount_pct"]')) > 0:
            # Game has a discount
            discount_pct = discount_div[0].xpath('.//div[@class="discount_pct"]/text()')[0]
            original_price = regex.sub(r'\p{Sc}', '',
                                       discount_div[0].xpath('.//div[@class="discount_original_price"]/text()')[0]).strip()
            final_price = regex.sub(r'\p{Sc}', '',
                                    discount_div[0].xpath('.//div[@class="discount_final_price"]/text()')[0]).strip()
        else:
            # Game doesn't have a discount
            discount_pct = "0%"

            # Try different price selectors for non-discounted games
            price_div = item.xpath('.//div[contains(@class, "discount_final_price")]')
            if price_div and price_div[0].text_content().strip():
                price = regex.sub(r'\p{Sc}', '', price_div[0].text_content()).strip()
            else:
                # Regular price container
                price_div = item.xpath('.//div[@class="tab_item_price"]')
                if price_div and price_div[0].text_content().strip():
                    price = regex.sub(r'\p{Sc}', '', price_div[0].text_content()).strip()
                else:
                    # Handle special cases like "Free", "Free to Play", or "Coming Soon"
                    special_text = item.xpath('.//div[contains(@class, "tab_item_price")]/text()')
                    price = special_text[0].strip() if special_text else "N/A"

            # For non-discounted games, original and final prices are the same
            original_price = price
            final_price = price

            # Check if this is "Free" or "Free to Play"
            if "free" in original_price.lower():
                original_price = "0"
                final_price = "0"

        # Create Game object
        game = Game(title, original_price, final_price, discount_pct, tags, platforms)
        games.append(game)

    return games

@app.route('/api/steam/new_releases', methods=['GET'])
def get_new_releases():
    url = request.args.get('url')
    tag = request.args.get('tag')
    platform = request.args.get('platform')
    discounted = request.args.get('discount_only', 'false').lower() == 'true'

    games = convert_to_dict(scrape_games())

    if isinstance(games, list):  # Make sure we have a game list, not an error
        if tag:
            games = [game for game in games if tag.lower() in [t.lower() for t in game['tags']]]

        if platform:
            games = [game for game in games if platform.lower() in [p.lower() for p in game['platforms']]]

        if discounted:
            games = [game for game in games if game['discount_pct'] != "0%"]

    return jsonify(games)

def convert_to_dict(games):
    return [game.__dict__ for game in games]

# Serialize to JSON
def main():
    games = scrape_games()
    print(json.dumps(convert_to_dict(games), indent=2))

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == "server":
        app.run(debug=True, port=5000)
    else:
        main()
