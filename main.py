from telebot import TeleBot, custom_filters
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import sqlite3
from contextlib import closing

from database import (init_db, get_user_id, get_daily, get_month, insert_ignore)
from config import API_TOKEN, database_name
from utils import merge_tuples

# Define the states for the bot
class ReportState(StatesGroup):
    study_hours = State()
    award_points = State()

# Initialize state storage
state_storage = StateMemoryStorage()

# Initialize the bot with your token
bot = TeleBot(API_TOKEN, parse_mode='HTML', state_storage=state_storage)

# Initialize the database
init_db()

# Create the keyboard menu
def create_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton('/help'))
    markup.add(KeyboardButton('/report'))
    markup.add(KeyboardButton('/daily'), KeyboardButton('/month'))
    markup.add(KeyboardButton('/award'))
    return markup

# /start command handler with menu
@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    welcome_text = "Welcome! Use the menu below to interact with the bot."
    bot.send_message(message.chat.id, welcome_text, reply_markup=create_menu())

# /help command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "It has only 4 commands:\n\n"
        "🔶 /report\n"
        "- Bot asks you, friend, how much did you focus today?\n"
        "- You just write the number (doesn’t need to reply).\n"
        "- Bot answers, thank you! your study time has been recorded.\n\n"
        "🔶 /award\n"
        "- Use the /award button to award points. The bot will prompt you to provide the username and points.\n\n"
        "🔶 /daily\n"
        "- Anyone who liked, by giving this command will give us the study hours and scores of all the members with a ranking based on the most study hours.\n\n"
        "🔶 /month\n"
        "- At the end of the month, anyone who wants to give this order will give us the ranking of all members based on overall score."
    )
    bot.send_message(message.chat.id, help_text)

# Record study time
@bot.message_handler(commands=['report'])
def ask_study_time(message: Message):
    insert_ignore(message.from_user.id, message.from_user.first_name, message.from_user.username)
    bot.reply_to(message, "Friend, how much did you focus today?")
    bot.set_state(message.from_user.id, ReportState.study_hours, message.chat.id)

@bot.message_handler(state=ReportState.study_hours)
def save_study_time(message: Message):
    bot.delete_state(message.from_user.id, message.chat.id)
    try:
        hours = int(message.text)
    except ValueError:
        bot.reply_to(message, "Please enter a valid number of hours.")
        return

    with sqlite3.Connection(database_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('INSERT INTO study_hours (hours, user_id) VALUES (?, ?)', (hours, message.from_user.id))
            cursor.execute('UPDATE users SET total_hours = total_hours + ?', (hours,))
            conn.commit()

    bot.reply_to(message, "Thank you! Your study time has been recorded.")

# /award command handler
@bot.message_handler(commands=['award'])
def ask_award_details(message: Message):
    bot.reply_to(message, "Oh well, who is going to get the point?  in the format: @username points")
    bot.set_state(message.from_user.id, ReportState.award_points, message.chat.id)

@bot.message_handler(state=ReportState.award_points)
def process_award(message: Message):
    bot.delete_state(message.from_user.id, message.chat.id)

    try:
        # Extract username and points from the message
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].isdigit() or not parts[0].startswith('@'):
            bot.reply_to(message, "Invalid format. Please use: @username points")
            return

        username = parts[0].strip('@')
        points = int(parts[1])

        user_id = get_user_id(username=username)

        if user_id:
            giver_name = message.from_user.username or message.from_user.id

            with sqlite3.Connection(database_name) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('INSERT INTO points_awards (giver, points, user_id) VALUES (?, ?, ?)', (giver_name, points, user_id[0]))
                    conn.commit()

            bot.reply_to(message, f"{points}💎 points have been awarded to @{username}!")
        else:
            bot.reply_to(message, "Username not found. Please check and try again.")

    except Exception as e:
        bot.reply_to(message, "An error occurred while processing the award.")

# Generate a daily report for daily progress and overall score
@bot.message_handler(commands=['daily'])
def send_daily_progress_report(message):
    results = get_daily()
    results.sort(key=lambda x: x[3], reverse=True)  # Sort by hours focused today
    month = merge_tuples(get_month())

    report = ""

    for i, row in enumerate(results, start=1):
        name, username, _, total_hours_today = row
        total_hours_month = month[name][2]
        total_points_month = month[name][1]
        overall_score = total_hours_month + total_points_month
        report += (f"Rank {i}:\n"
                   f"User: {name} (@{username})\n"
                   f"Hours of Focus Today: {total_hours_today}\n"
                   f"Overall Score This Month: {overall_score}💎 (Total Hours: {total_hours_month}, Points: {total_points_month}💎)\n\n")
    
    if report:
        bot.reply_to(message, f"📊 Daily Progress Report:\n\n{report}")
    else:
        bot.reply_to(message, "No data available for the report.")

# Generate a monthly report
@bot.message_handler(commands=['month'])
def generate_monthly_report(message):
    results = get_month()
    # Sort the results by overall score (total_points_month + total_hours_month) in descending order
    results.sort(key=lambda x: x[2] + x[3], reverse=True)

    report = ""
    
    for i, row in enumerate(results, start=1):
        name, username, total_points_month, total_hours_month = row
        overall_score = total_points_month + total_hours_month
        report += (f"Rank {i}:\n"
                   f"User: {name} (@{username})\n"
                   f"Monthly Report:\n"
                   f"Total Study Hours: {total_hours_month}\n"
                   f"Total Points: {total_points_month}💎\n"
                   f"Overall Score: {overall_score}💎\n\n")
    
    if report:
        bot.reply_to(message, f"📅 Monthly Report:\n\n{report}")
    else:
        bot.reply_to(message, "No data available for the monthly report.")

# Run the bot
if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)
