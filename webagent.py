from typing import Dict, List
from autogen import ConversableAgent
import os
import re
import praw
import requests

# Fetch Car Data from Reddit
def fetch_car_data(car_model: str) -> Dict[str, List[str]]:
    print(f"Fetching car data for: {car_model}")
    normalized_input = re.sub(r'[^a-zA-Z0-9]', '', car_model).lower()

    reddit = praw.Reddit(
        # client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_id='lw-HvQk3g6qXmAh02Qjo_A',
        client_secret='ga9rnhrBSdLipwE50qCL7ktmSE1bAg',
        user_agent="car_review_scraper"
    )

    subreddit = reddit.subreddit("cars")
    reviews = []
    seen_titles = set()

    for submission in subreddit.search(car_model, limit=20):
        normalized_title = re.sub(r'[^a-zA-Z0-9]', '', submission.title).lower()
        if normalized_input in normalized_title and submission.title not in seen_titles:
            seen_titles.add(submission.title)
            if submission.selftext.strip():
                reviews.append(submission.selftext.strip())
            elif submission.title.strip():
                reviews.append(submission.title.strip())
            submission.comments.replace_more(limit=0)
            for comment in submission.comments[:3]:
                reviews.append(comment.body.strip())
    print(f"Found {len(reviews)} Reddit reviews.")
    return {car_model: reviews}

# Fetch Car Data from Bing Web Search
def fetch_web_data(car_model: str) -> Dict[str, List[str]]:
    print(f"Fetching web search results for: {car_model}")
    bing_api_key = 'de4d3772ac894cf28faabe9b37ae2256'
    if not bing_api_key:
        raise ValueError("BING_API_KEY environment variable is not set.")

    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
    params = {"q": f"{car_model} reviews opinions pros cons", "count": 5}

    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code != 200:
        raise ValueError(f"Error fetching Bing API: {response.status_code} {response.text}")

    data = response.json()
    summaries = []

    for web_result in data.get("webPages", {}).get("value", []):
        summaries.append(f"{web_result['name']}: {web_result['snippet']}")

    print(f"Found {len(summaries)} web search results.")
    return {car_model: summaries}

# Summarize Reviews using GPT-4
def summarize_reviews_via_llm(reviews: List[str], llm_config) -> List[str]:
    from autogen import OpenAIWrapper

    model = OpenAIWrapper(api_key='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', model=llm_config["config_list"][0]["model"])

    prompt = f"""
    Here are reviews and opinions about a car model:
    {reviews}

    Summarize the key points about performance, features, reliability, and user feedback.
    """

    response = model.create(
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content
    summary = content.split("\n")

    return [line.strip() for line in summary if line.strip()]

# Main Function
def summarize_online_and_review_data(user_query: str):
    llm_config = {"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    try:
        # Fetch data from Reddit
        reddit_result = fetch_car_data(user_query)
        reddit_reviews = reddit_result[user_query]

        # Fetch data from Web
        web_result = fetch_web_data(user_query)
        web_reviews = web_result[user_query]

        print(f"\nTotal reviews collected: {len(reddit_reviews) + len(web_reviews)}")

        # Print Reddit Reviews
        print("\n--- Reddit Reviews ---")
        if reddit_reviews:
            for review in reddit_reviews:
                print(f"- {review}")
        else:
            print("No Reddit reviews found.")

        # Print Web Search Reviews
        print("\n--- Web Search Reviews ---")
        if web_reviews:
            for review in web_reviews:
                print(f"- {review}")
        else:
            print("No web search reviews found.")

        # Combine reviews and summarize via GPT-4
        combined_content = "\n".join(reddit_reviews + web_reviews)
        summarized_reviews = summarize_reviews_via_llm([combined_content], llm_config)
        return summarized_reviews

        # Print Final Summary
        print("\n--- Final Summary of Reviews ---")
        for line in summarized_reviews:
            print(f"- {line}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import sys
    assert len(sys.argv) > 1, "Please provide a query for a car model."
    main(sys.argv[1])