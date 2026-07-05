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
    return all_reviews


if __name__ == "__main__":
    reviews = scrape_amazon_reviews("laptop")
    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv("amazon_reviews.csv", index=False)
        print(f"Saved {len(df)} reviews to amazon_reviews.csv")
    else:
        print("No reviews saved")