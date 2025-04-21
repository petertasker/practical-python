import requests
import os
import sys
import shutil
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from newspaper import Article
from transformers import pipeline


def download_images(article):
    target_width, target_height = 1080, 1920
    target_ratio = target_width / target_height

    image_url = article.top_image
    image_blob = requests.get(image_url)

    # Save the original image first to ensure it's available for cropping
    with open("original_image.jpg", "wb") as file:
        file.write(image_blob.content)
    print("Downloaded original image: original_image.jpg")  # Debugging

    with Image(filename="original_image.jpg") as img:
        orig_width, orig_height = img.width, img.height
        orig_ratio = orig_width / orig_height

        def crop_and_save(offset_x, offset_y, width, height, name_suffix):
            with img.clone() as clone:
                clone.crop(offset_x, offset_y, width=width, height=height)
                clone.resize(target_width, target_height)
                filename = f"cropped_1_{name_suffix}.jpg"
                clone.save(filename=filename)
                print(f"Saved cropped image: {filename}")  # Debugging

        if orig_ratio > target_ratio:
            # Wider image – crop width
            new_width = int(orig_height * target_ratio)
            crop_and_save((orig_width - new_width) // 2, 0, new_width, orig_height, "center")
            crop_and_save(0, 0, new_width, orig_height, "left")
            crop_and_save(orig_width - new_width, 0, new_width, orig_height, "right")
        else:
            # Taller image – crop height
            new_height = int(orig_width / target_ratio)
            crop_and_save(0, (orig_height - new_height) // 2, orig_width, new_height, "center")
            crop_and_save(0, 0, orig_width, new_height, "top")
            crop_and_save(0, orig_height - new_height, orig_width, new_height, "bottom")


def caption_images(text, filename="cropped_1.jpg", text_start_percentage=0.15):
    with Image(filename=filename) as image:
        # Font settings
        draw_shadow = Drawing()
        draw_shadow.font = "Arial-Black"
        draw_shadow.font_size = 53
        draw_shadow.fill_color = Color("black")

        draw = Drawing()
        draw.font = "Arial-Black"
        draw.font_size = 53
        draw.fill_color = Color("white")

        # Text position
        text_y_start = int(image.height * text_start_percentage)
        padding = 40
        max_width = image.width - (padding * 2)

        # Break text into lines that fit the width
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            metrics = draw.get_font_metrics(image, test_line)

            if metrics.text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        # Add the last line
        if current_line:
            lines.append(current_line)

        # Draw text lines at the specified position
        y_position = text_y_start
        line_height = 50
        shadow_offset = 3

        for line in lines:
            metrics = draw.get_font_metrics(image, line)
            x_position = int((image.width - metrics.text_width) / 2)

            # Draw shadow with offset
            draw_shadow.text(x_position + shadow_offset, y_position + shadow_offset, line)
            draw_shadow(image)

            # Draw main text
            draw.text(x_position, y_position, line)
            draw(image)

            y_position += line_height

        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)

        output_filename = os.path.join(output_folder,
                                       filename.replace(".jpg", f"_text_{int(text_start_percentage * 100)}%.jpg"))
        image.save(filename=output_filename)


def summarise_article(article):
    text = article.text
    summariser = pipeline("summarization", model="facebook/bart-large-cnn")
    max_chunk = 1024

    if len(text) > max_chunk:
        text = text[:max_chunk]

    # AI summary of the article
    summary = summariser(text, max_length=150, min_length=20, do_sample=True)
    return summary[0]['summary_text']


def scrape_article(article_url):
    try:
        # Scrape and parse article
        article = Article(article_url)
        article.download()
        article.parse()
        return article
    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print("Did you add an article?")
        sys.exit(1)

    article_url = sys.argv[1]
    article = scrape_article(article_url)

    if not article:
        print("Did you add an article?")
        sys.exit(1)

    # Download and crop the article's header image
    download_images(article)

    # Use ML to provide a brief summary of the article
    summary = summarise_article(article)

    # Find applicable saved images to draw a caption on top of
    suffixes = []
    for suffix in ["center", "left", "right", "top", "bottom"]:
        if os.path.exists(f"cropped_1_{suffix}.jpg"):
            suffixes.append(suffix)

    # Caption each image
    for suffix in suffixes:
        print(f"Processing image with suffix: {suffix}")
        caption_images(summary, filename=f"cropped_1_{suffix}.jpg", text_start_percentage=0.15)
        caption_images(summary, filename=f"cropped_1_{suffix}.jpg", text_start_percentage=0.7)

    print(f"Summarised article: {summary}")

    # Clean up
    for suffix in suffixes:
        try:
            os.remove(f"cropped_1_{suffix}.jpg")
        except OSError:
            pass
    try:
        os.remove("original_image.jpg")
    except OSError:
        pass
if __name__ == "__main__":
    main()