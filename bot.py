import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ==============================
# 🔐 PASTE YOUR DETAILS HERE
# ==============================

BOT_TOKEN = "8326238730:AAGGtX6TdaQD0TedzpQATRnRAdulGQ9kHIw"

HISTORY_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

CURRENT_API = "https://draw.ar-lottery01.com/WinGo/WinGo_1M.json"

# ==============================


def classify(number):
    number = int(number)
    return "BIG" if number >= 5 else "SMALL"


def get_last_10():
    response = requests.get(HISTORY_API)
    data = response.json()
    results = data["data"]["list"]
    numbers = [int(item["number"]) for item in results]
    return numbers


def get_current_issue():
    response = requests.get(CURRENT_API)
    data = response.json()
    return data["current"]["issueNumber"]


def predict(numbers):
    results = [classify(n) for n in numbers]

    score_big = 0
    score_small = 0

    # Reverse 3 streak
    if len(results) >= 3 and len(set(results[:3])) == 1:
        if results[0] == "BIG":
            score_small += 3
        else:
            score_big += 3

    # Reverse strong majority
    if results.count("BIG") >= 7:
        score_small += 2
    if results.count("SMALL") >= 7:
        score_big += 2

    # Fallback reverse last
    if score_big == 0 and score_small == 0:
        if results[0] == "BIG":
            score_small += 1
        else:
            score_big += 1

    prediction = "BIG" if score_big > score_small else "SMALL"
    confidence = min(60 + abs(score_big - score_small) * 10, 95)

    return prediction, confidence


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔥 Live Prediction", callback_data="live")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to WinGo Prediction Bot\n\nClick below for live signal:",
        reply_markup=reply_markup
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        numbers = get_last_10()
        issue = get_current_issue()
        prediction, confidence = predict(numbers)

        message = f"""
🔥 WIN GO 1M LIVE PREDICTION 🔥

🕒 Period: {issue}
📊 SIGNAL: {prediction}
🎯 Confidence: {confidence}%

━━━━━━━━━━━━━━━━
⚠️ Maintain 6 Level Funds
💰 Trade With Proper Risk Management
━━━━━━━━━━━━━━━━
"""

        await query.edit_message_text(text=message)

    except Exception as e:
        await query.edit_message_text("⚠️ Error fetching data. Try again.")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

print("Bot is running...")

app.run_polling()
