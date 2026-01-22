import os
import time
import json
import requests
from dotenv import load_dotenv
from telegram import Bot
import html
from requests.exceptions import HTTPError


# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
CSRF_TOKEN = os.getenv("CSRF_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Proxy configuration (take details from env). Support either a full PROXY_URL
# or components: PROXY_USER, PROXY_PASS, PROXY_HOST, PROXY_PORT
PROXY_URL = os.getenv("PROXY_URL")
if not PROXY_URL:
    PROXY_USER = os.getenv("PROXY_USER")
    PROXY_PASS = os.getenv("PROXY_PASS")
    PROXY_HOST = os.getenv("PROXY_HOST")
    PROXY_PORT = os.getenv("PROXY_PORT")
    if PROXY_HOST and PROXY_PORT:
        auth = f"{PROXY_USER}:{PROXY_PASS}@" if PROXY_USER and PROXY_PASS else ""
        PROXY_URL = f"http://{auth}{PROXY_HOST}:{PROXY_PORT}"

PROXIES = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None

# Log proxy usage at startup
if PROXIES:
    print(f"Using proxy: {PROXY_URL}")
else:
    print("No proxy configured. Requests will be made directly.")

# Requests TLS verification handling:
# - If REQUESTS_CA_BUNDLE is set, requests will use that bundle path for verification.
# - If REQUESTS_VERIFY is explicitly 'false' or '0', verification will be disabled (not recommended).
REQUESTS_CA_BUNDLE = os.getenv("REQUESTS_CA_BUNDLE")
_requests_verify_env = os.getenv("REQUESTS_VERIFY")
if REQUESTS_CA_BUNDLE:
    VERIFY = REQUESTS_CA_BUNDLE
elif _requests_verify_env and _requests_verify_env.lower() in ("0", "false", "no"):
    VERIFY = False
else:
    VERIFY = True

# Load user mappings from config file
with open("config.json") as f:
    user_ids = json.load(f)


# Initialize bot
BOT = Bot(BOT_TOKEN)


def get_tweets(user_id, retry_count=0, max_retries=3):
    """Fetch recent tweets from a given user ID with rate limit handling."""
    url = "https://x.com/i/api/graphql/Wms1GvIiHXAPBaCr9KblaA/UserTweets"
    params = {
    'variables': '{{"userId":"{userid}","count":20,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withVoice":true}}'.format(userid=user_id),
    'features': '{"rweb_video_screen_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"responsive_web_profile_redirect_enabled":false,"rweb_tipjar_consumption_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":true,"responsive_web_jetfuel_frame":true,"responsive_web_grok_share_attachment_enabled":true,"responsive_web_grok_annotations_enabled":false,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"responsive_web_grok_show_grok_translated_post":false,"responsive_web_grok_analysis_button_from_backend":true,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_grok_imagine_annotation_enabled":true,"responsive_web_grok_community_note_auto_translation_is_enabled":false,"responsive_web_enhance_cards_enabled":false}',
    'fieldToggles': '{"withArticlePlainText":false}',
}
    headers = {
        'authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-csrf-token': CSRF_TOKEN,
    }
    cookies = {
        'auth_token': AUTH_TOKEN,
        'ct0': CSRF_TOKEN,
    }

    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers, timeout=30, verify=VERIFY,proxies=PROXIES)
        response.raise_for_status()
        data = response.json()['data']['user']['result']['timeline']['timeline']['instructions'][-1]['entries']
        data_dict = {}
        for tweet in data:
            if not tweet['entryId'].startswith('tweet-'):
                continue
            try:
                if 'tweet_results' in tweet['content']['itemContent']:
                    tweet_id = tweet['content']['itemContent']['tweet_results']['result']['legacy']['id_str']
                    data_dict[tweet_id] = tweet['content']['itemContent']['tweet_results']
                    return dict(list(data_dict.items())[:1])

                else:
                    tweet_id = tweet['content']['itemContent']['tweet']['result']['legacy']['id_str']
                    data_dict[tweet_id] = tweet['content']['itemContent']['retweeted_status_result']
                    return dict(list(data_dict.items())[:1])
            except KeyError:
                pass
    except HTTPError as e:
        if e.response.status_code == 429:
            # Rate limit hit - implement exponential backoff
            if retry_count < max_retries:
                wait_time = (2 ** retry_count) * 60  # 60s, 120s, 240s
                print(f"WARNING: Rate limit hit for user {user_id}. Waiting {wait_time} seconds before retry {retry_count + 1}/{max_retries}")
                time.sleep(wait_time)
                return get_tweets(user_id, retry_count + 1, max_retries)
            else:
                print(f"ERROR: Rate limit hit for user {user_id}. Max retries reached. Skipping this user for now.")
                return {}
        else:
            print(f"ERROR: HTTP Error fetching tweets for user {user_id}: {e}")
            return {}
    except requests.RequestException as e:
        print(f"ERROR: Error fetching tweets for user {user_id}: {e}")
        return {}


def tweet_to_telegram(tweet_json, username):
    """Send a tweet to the Telegram channel."""
    tweet_content = tweet_json.get('result', {}).get('legacy', tweet_json)
    caption = f"Tweet by {username}\n\n{html.unescape(tweet_content['full_text'])}"
    media = tweet_content.get('entities', {}).get('media', [{}])[0].get('media_url_https')

    try:
        if media:
            BOT.send_photo(chat_id=CHAT_ID, photo=media, caption=caption)
        else:
            BOT.send_message(chat_id=CHAT_ID, text=caption)
    except Exception as e:
        print(f"ERROR: Error sending message to Telegram: {e}")


def monitor_tweets():
    """Continuously monitor and send new tweets."""
    print("Starting tweet monitoring...")
    
    # Initialize old_tweets with delay between users to avoid rate limits
    old_tweets = {}
    for i, user_id in enumerate(user_ids):
        print(f"Fetching initial tweets for user {user_ids[user_id]} ({i+1}/{len(user_ids)})")
        old_tweets[user_id] = get_tweets(user_id)
        # Add delay between initial requests to avoid rate limiting
        if i < len(user_ids) - 1:  # Don't sleep after the last user
            time.sleep(5)
    
    print("Initial tweet fetch complete. Starting monitoring loop...")
    
    while True:
        for user_id, username in user_ids.items():
            try:
                new_tweets = get_tweets(user_id)
            except Exception as e:
                print(f"ERROR: Error fetching tweets for {username}: {e}")
                continue
            
            # Check for new tweets
            for tweet_id, tweet_data in new_tweets.items():
                if tweet_id not in old_tweets[user_id]:
                    try:
                        tweet_to_telegram(tweet_data, username)
                        old_tweets[user_id][tweet_id] = tweet_data
                        print(f"Sent new tweet from {username}: {tweet_id}")
                    except Exception as e:
                        print(f"ERROR: Error processing tweet from {username}: {e}")
            
            # Add delay between users to avoid rate limits
            time.sleep(10)
        
        # Wait before next cycle
        print("Completed monitoring cycle. Waiting 30 seconds...")
        time.sleep(30)


if __name__ == "__main__":
    monitor_tweets()
