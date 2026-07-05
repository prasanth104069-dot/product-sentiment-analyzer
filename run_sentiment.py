import pandas as pd
from sentiment import analyze_text

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)

    # Auto-detect the product column, whatever it's named
    id_col = None
    for col in ["product_id", "product_name", "product"]:
        if col in df.columns:
            id_col = col
            break
    if id_col is None:
        id_col = df.columns[0]  # fallback: just use the first column

    # Auto-detect the review text column
    text_col = None
    for col in ["review_text", "review", "text"]:
        if col in df.columns:
            text_col = col
            break
    if text_col is None:
        text_col = df.columns[-1]  # fallback: last column

    results = []
    for _, row in df.iterrows():
        analysis = analyze_text(str(row[text_col]))
        results.append({
            "product_id": row[id_col],
            "review_text": row[text_col],
            "sentiment": analysis["overall_sentiment"],
            "confidence": analysis["confidence"],
            "positive_score": analysis["scores"]["positive"],
            "negative_score": analysis["scores"]["negative"],
            "neutral_score": analysis["scores"]["neutral"],
        })

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False)
    print(f"Saved {len(result_df)} analyzed reviews to {output_file}")
    print(result_df["sentiment"].value_counts())


if __name__ == "__main__":
    process_csv("flipkart_reviews.csv", "flipkart_reviews_analyzed.csv")
    process_csv("amazon_reviews.csv", "amazon_reviews_analyzed.csv")