import os, requests, schedule, time
from telegram.ext import Updater, CommandHandler
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Telegram and Twilio Auth
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))

def get_top_coin_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False
    }
    res = requests.get(url, params=params).json()
    return "\n".join([f"{c['name']}: ${c['current_price']} ({c['price_change_percentage_24h']:.2f}%)" for c in res])

def get_crypto_news():
    key = os.getenv("CRYPTOPANIC_API")
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={key}&filter=trending"
    res = requests.get(url).json()
    return "\n\n".join([f"📰 {n['title']}\n🔗 {n['url']}" for n in res['results'][:5]])

def send_to_whatsapp():
    msg = f"💰 Top 10 Crypto:\n\n{get_top_coin_prices()}\n\n📰 News:\n\n{get_crypto_news()}"
    client.messages.create(
        from_=os.getenv("FROM_WA"),
        to=os.getenv("TO_WA"),
        body=msg
    )
    print("✅ Sent to WhatsApp")

# Telegram /crypto trigger
def crypto(update, context):
    update.message.reply_text("⏳ Sending crypto news to your WhatsApp...")
    send_to_whatsapp()

updater = Updater(TELEGRAM_TOKEN)
updater.dispatcher.add_handler(CommandHandler("crypto", crypto))

# Scheduler every 30 mins
schedule.every(30).minutes.do(send_to_whatsapp)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start everything
import threading
threading.Thread(target=run_schedule).start()
updater.start_polling()
