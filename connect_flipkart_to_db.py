# connect_flipkart_to_db.py
# Bridges Team 3's Flipkart scraper + sentiment with Team 4's database
# Run this to scrape a product from Flipkart and save results to PostgreSQL

import sys
from flipkart_scraper import scrape_flipkart_reviews
from database import save_product, save_reviews

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    print("[WARNING] TextBlob not installed. Run: pip install textblob")


def get_sentiment(text):
    """Analyze sentiment of a review text."""
    if HAS_TEXTBLOB:
        blob = TextBlob(text)
        score = blob.sentiment.polarity

        if score > 0.1:
            label = "Positive"
        elif score < -0.1:
            label = "Negative"
        else:
            label = "Neutral"

        return label, round(score, 2)

    return "Neutral", 0.0


def scrape_and_save(product_name):
    """
    1. Scrapes Flipkart for the product
    2. Analyzes sentiment for each review
    3. Saves everything to PostgreSQL database
    """
    print(f"\n{'='*50}")
    print(f"Scraping Flipkart for: {product_name}")
    print(f"{'='*50}\n")

    raw_reviews, real_title, image_url, specs = scrape_amazon_reviews(product_name)

    if not raw_reviews:
        print("[ERROR] No reviews scraped. Try a different product name.")
        return False

    print(f"[OK] Scraped {len(raw_reviews)} review snippets")

    processed_reviews = []
    for r in raw_reviews:
        text = r["review_text"]
        sentiment, score = get_sentiment(text)

        processed_reviews.append({
            "title": text[:60] + "..." if len(text) > 60 else text,
            "body": text,
            "rating": "N/A",
            "date": "N/A",
            "sentiment": sentiment,
            "sentiment_score": score
        })

    product_id = save_product(
        product_name=product_name,
        source="flipkart",
        title=raw_reviews[0]["product_name"],
        price="N/A",
        overall_rating="N/A",
        total_reviews=str(len(processed_reviews))
    )

    if not product_id:
        print("[ERROR] Could not save product to database")
        return False

    success = save_reviews(product_id, product_name, "flipkart", processed_reviews)

    if success:
        pos = sum(1 for r in processed_reviews if r["sentiment"] == "Positive")
        neg = sum(1 for r in processed_reviews if r["sentiment"] == "Negative")
        neu = sum(1 for r in processed_reviews if r["sentiment"] == "Neutral")

        print(f"\n{'='*50}")
        print(f"DONE! Saved to database:")
        print(f"   Product: {product_name}")
        print(f"   Source: Flipkart")
        print(f"   Total reviews: {len(processed_reviews)}")
        print(f"   Positive: {pos} | Negative: {neg} | Neutral: {neu}")
        print(f"{'='*50}\n")
        return True

    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        product = sys.argv[1]
    else:
        product = input("Enter product name to scrape from Flipkart (e.g. 'iphone 15'): ")

    scrape_and_save(product)