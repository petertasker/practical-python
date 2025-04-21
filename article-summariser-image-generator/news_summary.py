import requests
from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing
from newspaper import Article
from transformers import pipeline


def caption_images(text, filename="cropped_1.jpg"):
    with Image(filename=filename) as image:
        # Font settings
        draw_shadow = Drawing()
        draw_shadow.font = "Arial-Black"
        draw_shadow.font_size = 80
        draw_shadow.fill_color = Color("black")

        draw = Drawing()
        draw.font = "Arial-Black"
        draw.font_size = 80
        draw.fill_color = Color("white")

        # Text position
        text_y_start = int(image.height * 0.15)
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
        line_height = 100  # Increased spacing between lines
        shadow_offset = 3  # Pixels to offset shadow

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

        image.save(filename=filename.replace(".jpg", "_text.jpg"))

def summarise_article(article):
    text = article.text
    summariser = pipeline("summarization", model="facebook/bart-large-cnn")
    max_chunk = 1024

    if len(text) > max_chunk:
        text = text[:max_chunk]

    # AI summary of the article
    summary = summariser(text, max_length=50, min_length=20, do_sample=False)
    return summary[0]['summary_text']


def download_images(article):
    target_width, target_height = 1080, 1920
    target_ratio = target_width / target_height

    image_url = article.top_image
    image_blob = requests.get(image_url)

    with Image(blob=image_blob.content) as img:
        orig_width, orig_height = img.width, img.height
        orig_ratio = orig_width / orig_height

        def crop_and_save(offset_x, offset_y, width, height, name_suffix):
            with img.clone() as clone:
                clone.crop(offset_x, offset_y, width=width, height=height)
                clone.resize(target_width, target_height)
                clone.save(filename=f"cropped_1_{name_suffix}.jpg")

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



def main():
    article_url = "https://www.newyorker.com/magazine/2004/05/10/torture-at-abu-ghraib"
    article = Article(article_url)
    article.download()
    article.parse()

    download_images(article)
    summary = summarise_article(article)

    suffixes = ["center", "top", "bottom"] if article.top_image else []
    for suffix in suffixes:
        caption_images(summary, filename=f"cropped_1_{suffix}.jpg")

    print(f"Summarised article: {summary}")



if __name__ == "__main__":
    main()

