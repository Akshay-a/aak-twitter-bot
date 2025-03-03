import tweepy
from datetime import datetime
from env import BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
# Replace these with your actual Twitter API credentials


# Authenticate with v2 Client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

def is_challenge_tweet(tweet_text):
    """Check if the tweet is part of a trading challenge."""
    challenge_keywords = ["$ to", "challenge"]
    return all(keyword.lower() in tweet_text.lower() for keyword in challenge_keywords)


"""
SAMPLE CHALLENGE TWEET format to be used for the function extract_entry_details(tweet_text):
150$-300$

Closing $BTC long 

Gained 24$

Now balance is 206$
"""
def extract_entry_details(tweet_text):
    """Extract challenge entry details from the tweet."""
    lines = tweet_text.split('\n')
    entry_details = {"challenge": None, "asset": None, "entries": [], "stop_loss": None}
    for line in lines:
        line = line.strip().lower()
        if "$" in line and ("to" in line or "-" in line) and "challenge" in line:
            entry_details["challenge"] = line.split("challenge")[0].strip()
        elif "$" in line and not any(x in line for x in ["entry", "sl"]):
            entry_details["asset"] = line.split()[1].strip("$")
        elif "entry" in line and any(char.isdigit() for char in line):
            price = ''.join(filter(str.isdigit, line))
            if price:
                entry_details["entries"].append(price)
        elif "sl" in line and any(char.isdigit() for char in line):
            price = ''.join(filter(str.isdigit, line))
            if price:
                entry_details["stop_loss"] = price
    return entry_details

def check_user_tweets(username="Crypto_Arki", count=5):
    """Fetch recent tweets from the user and validate challenge entries."""
    try:
        # Get user ID from username
        user = client.get_user(username=username)
        if not user.data:
            print(f"User {username} not found.")
            return

        # Fetch tweets using v2 endpoint
        tweets = client.get_users_tweets(id=user.data.id, max_results=count, tweet_fields=["created_at"])
        if not tweets.data:
            print(f"No tweets found for {username}.")
            return

        for tweet in tweets.data:
            tweet_text = tweet.text
            tweet_date = tweet.created_at
            if is_challenge_tweet(tweet_text):
                details = extract_entry_details(tweet_text)
                print(f"\nTweet Date: {tweet_date}")
                print(f"Tweet Text: {tweet_text}")
                print("Challenge Entry Details:")
                print(f"  Challenge: {details['challenge']}")
                print(f"  Asset: {details['asset']}")
                print(f"  Entries: {', '.join(details['entries'])}")
                print(f"  Stop Loss: {details['stop_loss']}")
    except tweepy.TweepyException as e:
        print(f"Error fetching tweets: {e}")

if __name__ == "__main__":
    print(f"Checking tweets as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_user_tweets("Crypto_Arki", 5)
 