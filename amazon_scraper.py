from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_amazon_reviews(search_term):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    all_reviews = []
    search_url = f"https://www.amazon.in/s?k={search_term}"
    driver.get(search_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_links = [a for a in soup.select("a.a-link-normal.s-no-outline") if a.get('href') and '/sspa/' not in a['href']]
    if not product_links:
        product_links = soup.select("h2 a.a-link-normal")

    product_url = "https://www.amazon.in" + product_links[0]['href']
    driver.get(product_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    try:
        product_name = soup.select_one("#productTitle").text.strip()
    except:
        product_name = search_term
    print("Product:", product_name)

    # 1) PRODUCT IMAGE
    image_url = "N/A"
    try:
        img_tag = soup.select_one("#imgTagWrapperId img") or soup.select_one("#landingImage")
        if img_tag:
            # Amazon sometimes hides the real high-res URL in data-old-hires
            image_url = img_tag.get("data-old-hires") or img_tag.get("src") or "N/A"
    except Exception:
        pass
    print("Image URL:", image_url)

    # 2) BASIC SPECS (battery, display, RAM, etc. — varies by product category)
    specs = {}
    try:
        spec_table = soup.select_one("#productDetails_techSpec_section_1") \
                     or soup.select_one("#detailBullets_feature_div") \
                     or soup.select_one("#poExpander")
        if spec_table:
            rows = spec_table.select("tr")
            for row in rows:
                key_el = row.select_one("th") or row.select_one(".a-text-bold")
                val_el = row.select_one("td")
                if key_el and val_el:
                    key = key_el.get_text(strip=True)
                    val = val_el.get_text(strip=True)
                    if key and val:
                        specs[key] = val
    except Exception:
        pass
    print("Specs found:", specs)

    # Scroll all the way down so lazy-loaded sections render
    for _ in range(15):
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(0.5)

    # IMPORTANT: take a fresh snapshot of the page AFTER scrolling is fully done,
    # then parse with BeautifulSoup (avoids stale element errors)
    final_html = driver.page_source
    soup = BeautifulSoup(final_html, "html.parser")

    candidates = soup.find_all(["span", "div"])
    print(f"Scanning {len(candidates)} elements from page snapshot")

    seen = set()
    junk_keywords = ["amazon", "sign in", "cart", "delivery", "return policy", "cookie", "javascript", "menu", "prime", "subscribe"]

    for el in candidates:
        text = el.get_text(strip=True)
        if 50 < len(text) < 1500 and text not in seen:
            if not any(j in text.lower()[:30] for j in junk_keywords):
                # skip if it contains nested block elements (avoid grabbing huge page chunks)
                if not el.find(["div", "span", "table"]):
                    seen.add(text)
                    all_reviews.append({"product_name": product_name, "review_text": text})

    driver.quit()
    return all_reviews, product_name, image_url, specs


if __name__ == "__main__":
    reviews, name, image_url, specs = scrape_amazon_reviews("laptop")
    print("Image:", image_url)
    print("Specs:", specs)
    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv("amazon_reviews.csv", index=False)
        print(f"Saved {len(df)} reviews to amazon_reviews.csv")
    else:
        print("No reviews saved")
