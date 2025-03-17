import os
import time
import json
import requests
import logging
from dotenv import load_dotenv
from telegram import Bot
import html

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
CSRF_TOKEN = os.getenv("CSRF_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Load user mappings from config file
with open("config.json") as f:
    user_ids = json.load(f)

# Initialize bot
BOT = Bot(BOT_TOKEN)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_tweets(user_id):
    """Fetch recent tweets from a given user ID."""
    url = "https://x.com/i/api/graphql/Y9WM4Id6UcGFE8Z-hbnixw/UserTweets"
    params = {
        'variables': json.dumps({"userId": user_id, "count": 50, "includePromotedContent": True,
                                 "withQuickPromoteEligibilityTweetFields": True, "withVoice": True,
                                 "withV2Timeline": True}),
        'features': json.dumps(
            {"profile_label_improvements_pcf_label_in_post_enabled": True, "rweb_tipjar_consumption_enabled": True,
             "responsive_web_graphql_exclude_directive_enabled": True, "verified_phone_label_enabled": False,
             "creator_subscriptions_tweet_preview_api_enabled": True,
             "responsive_web_graphql_timeline_navigation_enabled": True,
             "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
             "premium_content_api_read_enabled": False, "communities_web_enable_tweet_community_results_fetch": True,
             "c9s_tweet_anatomy_moderator_badge_enabled": True,
             "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
             "responsive_web_grok_analyze_post_followups_enabled": True, "responsive_web_jetfuel_frame": False,
             "responsive_web_grok_share_attachment_enabled": True, "articles_preview_enabled": True,
             "responsive_web_edit_tweet_api_enabled": True,
             "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
             "view_counts_everywhere_api_enabled": True, "longform_notetweets_consumption_enabled": True,
             "responsive_web_twitter_article_tweet_consumption_enabled": True,
             "tweet_awards_web_tipping_enabled": False, "responsive_web_grok_analysis_button_from_backend": True,
             "creator_subscriptions_quote_tweet_preview_enabled": False,
             "freedom_of_speech_not_reach_fetch_enabled": True, "standardized_nudges_misinfo": True,
             "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
             "rweb_video_timestamps_enabled": True, "longform_notetweets_rich_text_read_enabled": True,
             "longform_notetweets_inline_media_enabled": True, "responsive_web_grok_image_annotation_enabled": False,
             "responsive_web_enhance_cards_enabled": False}),
        'fieldToggles': json.dumps({"withArticlePlainText": False}),
    }
    headers = {
        'authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'x-csrf-token': CSRF_TOKEN,
    }
    cookies = {
        'auth_token': AUTH_TOKEN,
        'ct0': CSRF_TOKEN,
    }

    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        response.raise_for_status()
        data = response.json()['data']['user']['result']['timeline_v2']['timeline']['instructions'][-1]['entries']
        data_dict = {}
        for tweet in data:
            try:
                if 'tweet_results' in tweet['content']['itemContent']:
                    tweet_id = tweet['content']['itemContent']['tweet_results']['result']['legacy']['id_str']
                    data_dict[tweet_id] = tweet['content']['itemContent']['tweet_results']
                else:
                    tweet_id = tweet['content']['itemContent']['tweet']['result']['legacy']['id_str']
                    data_dict[tweet_id] = tweet['content']['itemContent']['retweeted_status_result']
            except KeyError:
                pass
        return data_dict
    except requests.RequestException as e:
        logging.error(f"Error fetching tweets: {e}")
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
        logging.error(f"Error sending message to Telegram: {e}")


def monitor_tweets():
    """Continuously monitor and send new tweets."""
    old_tweets = {user_id: get_tweets(user_id) for user_id in user_ids}
    while True:
        for user_id, username in user_ids.items():
            new_tweets = get_tweets(user_id)
            for tweet_id, tweet_data in new_tweets.items():
                if tweet_id not in old_tweets[user_id]:
                    tweet_to_telegram(tweet_data, username)
                    old_tweets[user_id][tweet_id] = tweet_data
            time.sleep(15)
        time.sleep(30)


if __name__ == "__main__":
    monitor_tweets()
