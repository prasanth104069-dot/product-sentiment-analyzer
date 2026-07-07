# database.py
# Product Sentiment Analyzer — Database Module
# Uses PostgreSQL via Supabase (free cloud)
# Team 4 — Database

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# ──────────────────────────────────────────────
#  CONFIG — Replace with your Supabase details
# ──────────────────────────────────────────────

DB_CONFIG = {
    "host":     "localhost",  # From Supabase dashboard
    "database": "sentipulse_db",
    "user":     "postgres",
    "password": "warrobots",           # From Supabase dashboard
    "port":     "5432"
}


# ──────────────────────────────────────────────
#  CONNECT TO DATABASE
# ──────────────────────────────────────────────

def get_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("[DB] Connected to Supabase PostgreSQL ✅")
        return conn
    except Exception as e:
        print(f"[DB] Connection failed ❌: {e}")
        return None


# ──────────────────────────────────────────────
#  CREATE TABLES
# ──────────────────────────────────────────────

def create_tables():
    """
    Creates two tables:
    1. products  — stores product info
    2. reviews   — stores reviews + sentiment results
    """
    conn = get_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()

        # Products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id              SERIAL PRIMARY KEY,
                product_name    VARCHAR(255) NOT NULL,
                source          VARCHAR(50),        -- 'amazon' or 'flipkart'
                title           TEXT,
                price           VARCHAR(50),
                overall_rating  VARCHAR(20),
                total_reviews   VARCHAR(50),
                scraped_at      TIMESTAMP DEFAULT NOW()
            );
        """)

        # Reviews table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id               SERIAL PRIMARY KEY,
                product_id       INT REFERENCES products(id) ON DELETE CASCADE,
                product_name     VARCHAR(255),
                source           VARCHAR(50),        -- 'amazon' or 'flipkart'
                review_title     TEXT,
                review_body      TEXT,
                review_rating    VARCHAR(20),
                review_date      VARCHAR(50),
                sentiment        VARCHAR(20),        -- 'Positive', 'Negative', 'Neutral'
                sentiment_score  FLOAT,
                created_at       TIMESTAMP DEFAULT NOW()
            );
        """)

        conn.commit()
        print("[DB] Tables created successfully ✅")

    except Exception as e:
        print(f"[DB] Error creating tables ❌: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────
#  SAVE PRODUCT
# ──────────────────────────────────────────────

def save_product(product_name, source, title, price, overall_rating, total_reviews):
    """
    Save product info to database.
    Returns product_id for linking reviews.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()

        # Check if product already exists
        cur.execute("""
            SELECT id FROM products
            WHERE product_name = %s AND source = %s
        """, (product_name, source))

        existing = cur.fetchone()
        if existing:
            print(f"[DB] Product already exists, ID: {existing[0]}")
            return existing[0]

        # Insert new product
        cur.execute("""
            INSERT INTO products (product_name, source, title, price, overall_rating, total_reviews)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (product_name, source, title, price, overall_rating, total_reviews))

        product_id = cur.fetchone()[0]
        conn.commit()
        print(f"[DB] Product saved, ID: {product_id} ✅")
        return product_id

    except Exception as e:
        print(f"[DB] Error saving product ❌: {e}")
        conn.rollback()
        return None

    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────
#  SAVE REVIEWS + SENTIMENT
# ──────────────────────────────────────────────

def save_reviews(product_id, product_name, source, reviews):
    """
    Save list of reviews with sentiment to database.

    reviews = [
        {
            "title": "Great phone",
            "body": "Amazing camera and battery",
            "rating": "5.0 out of 5",
            "date": "June 2025",
            "sentiment": "Positive",
            "sentiment_score": 0.85
        },
        ...
    ]
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        saved_count = 0

        for review in reviews:
            cur.execute("""
                INSERT INTO reviews 
                    (product_id, product_name, source, review_title, 
                     review_body, review_rating, review_date, 
                     sentiment, sentiment_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                product_id,
                product_name,
                source,
                review.get("title", ""),
                review.get("body", ""),
                review.get("rating", ""),
                review.get("date", ""),
                review.get("sentiment", "Neutral"),
                review.get("sentiment_score", 0.0)
            ))
            saved_count += 1

        conn.commit()
        print(f"[DB] {saved_count} reviews saved ✅")
        return True

    except Exception as e:
        print(f"[DB] Error saving reviews ❌: {e}")
        conn.rollback()
        return False

    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────
#  GET REVIEWS BY PRODUCT
# ──────────────────────────────────────────────

def get_reviews(product_name, source=None):
    """
    Fetch all reviews for a product from database.
    source: 'amazon', 'flipkart', or None (both)
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if source:
            cur.execute("""
                SELECT * FROM reviews
                WHERE product_name ILIKE %s AND source = %s
                ORDER BY created_at DESC
            """, (f"%{product_name}%", source))
        else:
            cur.execute("""
                SELECT * FROM reviews
                WHERE product_name ILIKE %s
                ORDER BY created_at DESC
            """, (f"%{product_name}%",))

        reviews = cur.fetchall()
        print(f"[DB] Found {len(reviews)} reviews for '{product_name}' ✅")
        return [dict(r) for r in reviews]

    except Exception as e:
        print(f"[DB] Error fetching reviews ❌: {e}")
        return []

    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────
#  GET SENTIMENT SUMMARY
# ──────────────────────────────────────────────

def get_sentiment_summary(product_name):
    """
    Returns sentiment count summary for a product.
    """
    conn = get_connection()
    if not conn:
        return {}

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                sentiment,
                COUNT(*) as count
            FROM reviews
            WHERE product_name ILIKE %s
            GROUP BY sentiment
        """, (f"%{product_name}%",))

        rows = cur.fetchall()
        summary = {"Positive": 0, "Negative": 0, "Neutral": 0, "total": 0}

        for row in rows:
            sentiment = row["sentiment"]
            count = row["count"]
            summary[sentiment] = count
            summary["total"] += count

        print(f"[DB] Sentiment summary: {summary} ✅")
        return summary

    except Exception as e:
        print(f"[DB] Error fetching summary ❌: {e}")
        return {}

    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────
#  GET ALL PRODUCTS
# ──────────────────────────────────────────────

def get_all_products():
    """Returns list of all scraped products."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY scraped_at DESC")
        products = cur.fetchall()
        return [dict(p) for p in products]

    except Exception as e:
        print(f"[DB] Error fetching products ❌: {e}")
        return []

    finally:
        cur.close()
        conn.close()


# ──────────────────────────────────────────────
#  MAIN FUNCTION — Called by Backend/Scraper
# ──────────────────────────────────────────────

def save_scraped_data(scraped_data, sentiment_results):
    """
    Main function called by backend after scraping.

    scraped_data = {
        "product_name": "iphone 15",
        "source": "amazon",
        "product_info": {
            "title": "Apple iPhone 15",
            "price": "₹69,999",
            "overall_rating": "4.2 out of 5",
            "total_ratings": "15,420"
        },
        "reviews": [...]
    }

    sentiment_results = [
        {"sentiment": "Positive", "sentiment_score": 0.85},
        ...
    ]
    """
    product_name = scraped_data.get("product_name", "")
    source       = scraped_data.get("source", "")
    info         = scraped_data.get("product_info", {})
    reviews      = scraped_data.get("reviews", [])

    # Save product
    product_id = save_product(
        product_name  = product_name,
        source        = source,
        title         = info.get("title", ""),
        price         = info.get("price", ""),
        overall_rating= info.get("overall_rating", ""),
        total_reviews = info.get("total_ratings", "")
    )

    if not product_id:
        return False

    # Merge sentiment results into reviews
    for i, review in enumerate(reviews):
        if i < len(sentiment_results):
            review["sentiment"]       = sentiment_results[i].get("sentiment", "Neutral")
            review["sentiment_score"] = sentiment_results[i].get("sentiment_score", 0.0)

    # Save reviews
    return save_reviews(product_id, product_name, source, reviews)


# ──────────────────────────────────────────────
#  TEST (run directly)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Testing Database Module ===")

    # Step 1 — Create tables
    create_tables()

    # Step 2 — Save a test product
    product_id = save_product(
        product_name   = "iphone 15",
        source         = "amazon",
        title          = "Apple iPhone 15 128GB",
        price          = "₹69,999",
        overall_rating = "4.2 out of 5",
        total_reviews  = "15,420"
    )

    # Step 3 — Save test reviews
    test_reviews = [
        {
            "title": "Amazing phone!",
            "body": "Best camera I have ever used. Battery lasts all day.",
            "rating": "5.0 out of 5",
            "date": "June 2025",
            "sentiment": "Positive",
            "sentiment_score": 0.92
        },
        {
            "title": "Overpriced",
            "body": "Not worth the price. Android is better.",
            "rating": "2.0 out of 5",
            "date": "May 2025",
            "sentiment": "Negative",
            "sentiment_score": -0.65
        },
        {
            "title": "Decent phone",
            "body": "Good but nothing special compared to last year.",
            "rating": "3.0 out of 5",
            "date": "April 2025",
            "sentiment": "Neutral",
            "sentiment_score": 0.05
        }
    ]

    save_reviews(product_id, "iphone 15", "amazon", test_reviews)

    # Step 4 — Fetch reviews
    reviews = get_reviews("iphone 15")
    print(f"\nFetched {len(reviews)} reviews")

    # Step 5 — Get sentiment summary
    summary = get_sentiment_summary("iphone 15")
    print(f"\nSentiment Summary: {summary}")