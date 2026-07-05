from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def scrape_flipkart_reviews(search_term):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    all_reviews = []
    
    search_url = f"https://www.flipkart.com/search?q={search_term}"
    driver.get(search_url)
    time.sleep(3)

    try:
        close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
        close_btn.click()
    except:
        pass

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_links = soup.select("a.CGtC98") or soup.select("a[href*='/p/']")
    product_url = "https://www.flipkart.com" + product_links[0]['href']

    driver.get(product_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    try:
        product_name = soup.select_one("span.VU-ZEz").text.strip()
    except:
        product_name = search_term

    reviews_url = product_url.replace("/p/", "/product-reviews/")
    driver.get(reviews_url)
    time.sleep(3)

    # Scroll multiple times to load more reviews
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 1200);")
        time.sleep(1)

    # Use the exact class you found
    review_elements = driver.find_elements(By.CSS_SELECTOR, "span.css-1jxf684")
    print(f"Found {len(review_elements)} review texts")

    for el in review_elements:
        text = el.text.strip()
        if text and len(text) > 10:
            all_reviews.append({
                "product_name": product_name,
                "review_text": text
            })

    driver.quit()
    return all_reviews


if __name__ == "__main__":
    reviews = scrape_flipkart_reviews("laptop")
    
    if reviews:
        df = pd.DataFrame(reviews)
        df = df.drop_duplicates(subset="review_text")
        df.to_csv("flipkart_reviews.csv", index=False)
        print(f"Saved {len(df)} reviews to flipkart_reviews.csv")
    else:
        print("No reviews found with this class - class name may be dynamic/session-specific")