 # Tweet2Telegram: Real-Time Twitter Alerts for Telegram Groups 🚀

  **Tweet2Telegram** is a powerful Python script that monitors specific Twitter users for new tweets and automatically forwards them to a Telegram group or channel in real-time. Perfect for staying updated with important tweets without missing a beat!

  ---

  ## Key Features

  - **Real-Time Monitoring**: Instantly detects and forwards new tweets from specified Twitter users.
  - **Telegram Integration**: Sends tweets directly to your Telegram group or channel.
  - **Customizable**: Easily add or remove Twitter users via the `config.json` file.
  - **Media Support**: Forwards tweets with images as photos with captions.
  - **Lightweight & Efficient**: Built with Python for simplicity and performance.

  ---

  ## Why Use Tweet2Telegram?

  - **Stay Updated**: Never miss important tweets from your favorite accounts.
  - **Automate Notifications**: Save time by automating tweet forwarding to Telegram.
  - **Customizable Alerts**: Choose which Twitter users to monitor and where to send notifications.
  - **Open Source**: Free to use, modify, and extend.

  ---

  ## Prerequisites

  Before you begin, ensure you have the following:

  - **Python 3.8+**: The script is written in Python.
  - **Telegram Bot**: Create a bot using [BotFather](https://core.telegram.org/bots#botfather) and obtain the bot token.
  - **Telegram Chat ID**: Obtain the chat ID of the group or channel where you want to receive notifications.
  ---

  ## Installation

  1. **Clone the repository**:
     ```bash
     git clone https://github.com/irfanbd4/Real-Time-Twitter-Alerts.git
     cd twitter-to-telegram-notifier
     ```

  2. **Install dependencies**:
     ```bash
     pip install -r requirements.txt
     ```

  3. **Set up environment variables**:
     - Rename `.env.example` to `.env`.
     - Fill in the required values:
       ```plaintext
       BOT_TOKEN=your_bot_token_here
       CHAT_ID=-100XXXXXXXXXX
       AUTH_TOKEN=your_auth_token_here
       CSRF_TOKEN=your_csrf_token_here
       TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
       ```

  4. **Configure Twitter users**:
     - Edit the `config.json` file to include the Twitter user IDs and their corresponding usernames:
       ```json
       {
           "729435789411618817": "@AdamMancini4",
           "59603406": "@NickTimiraos"
       }
       ```

  ### How to Get Twitter Tokens

  To obtain the required Twitter tokens (`AUTH_TOKEN`, `CSRF_TOKEN`, and `TWITTER_BEARER_TOKEN`), follow these steps:

  1. **Open Twitter** in your browser and log in to your account.
  2. **Open Developer Tools**:
     - Press `F12` or `Ctrl + Shift + I` (Windows/Linux) or `Cmd + Option + I` (Mac) to open the developer tools.
  3. **Go to the Network Tab**:
     - In the developer tools, navigate to the **Network** tab.
  4. **Find the Tokens**:
     - **For `AUTH_TOKEN`**:
       - Search for `auth_token` in the network requests. It will appear as a cookie.
     - **For `CSRF_TOKEN`**:
       - Search for `x-csrf-token` in the request headers.
     - **For `TWITTER_BEARER_TOKEN`**:
       - Search for `authorization` in the request headers. The value will start with `Bearer`.

  Once you have these tokens, add them to your `.env` file as described in the **Installation** section.

  ---

  ## Usage

  Run the script using Python:

  ```bash
  python main.py
  ```
The script will start monitoring the specified Twitter users and send new tweets to the configured Telegram group or channel.

## Configuration

### Environment Variables

  - `BOT_TOKEN`: Your Telegram bot token.
  - `CHAT_ID`: The chat ID of the Telegram group or channel.
  - `AUTH_TOKEN`: Your Twitter auth token.
  - `CSRF_TOKEN`: Your Twitter CSRF token.
  - `TWITTER_BEARER_TOKEN`: Your Twitter Bearer token.

### Config File

  - `config.json`: Contains a mapping of Twitter user IDs to their usernames. Add or remove users as needed.

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/irfanbd4/Real-Time-Twitter-Alerts/issues).

---

<h2 align="center">Visitors Counts👀</h2>
<a href="https://github.com/irfanbd4/Real-Time-Twitter-Alerts"><img alt="Cute Count" src="https://count.getloli.com/@Real-Time-Twitter-Alerts?name=Real-Time-Twitter-Alerts&theme=love-and-deepspace&padding=7&offset=0&align=top&scale=1&pixelated=1&darkmode=auto" /></a>


## 💖 Donate

### Bitcoin (BTC) / Bitcoin Cash(BCH)
`1HeYJ3QJCzcwmPyNv2nkfJiSRTcw8mdGq3`

### Ethereum (ERC20) / Binance Smart Chain (BEP20)
`0xb61e6253f3278a2e9827a9637c2a4bc81778061a`

### Litecoin (LTC)
`LWgsCnz2cE654zPTnABjSpQsiPewqDTYXj`

### Tron (TRC20)
`TVbak59FUsGLtCCCTzZhR9t1eWnZYBFRXZ`

---

## 📞 Contact Me

For any questions or suggestions, feel free to reach out to me on Telegram:

[![Contact on Telegram](https://img.shields.io/badge/Contact%20Me-Telegram-blue?style=for-the-badge&logo=telegram)](https://t.me/Irfanbd2)
