# Study Time Tracking Bot

A Telegram bot that helps users track their daily study time, award points to each other, and generate reports on daily and monthly study performance.

## Features
- **Track Study Time**: Users can report how much time they have studied each day.
- **Award Points**: Users can award points to each other based on their performance.
- **Daily Report**: Shows the ranking of all users based on their daily study hours and monthly performance.
- **Monthly Report**: Provides a ranking based on the total study hours and points accumulated throughout the month.

## Commands
- `/start` - Start interacting with the bot and open the menu.
- `/help` - Get help and understand how the bot works.
- `/report` - Report your study hours for the day.
- `/award` - Award points to another user in the format: `@username points`.
- `/daily` - View the daily report with rankings of study time and performance.
- `/month` - View the monthly report with rankings of total study hours and points.

## Getting Started

### Prerequisites
- Python 3.x
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- SQLite for database management

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/hadis11/study.bot.git
    cd study.bot
    ```

2. Install dependencies:
    ```bash
    pip install pyTelegramBotAPI
    ```

3. Set up the database:
    - Create an SQLite database using the provided `database.py` script.
    - You can initialize it with the `init_db()` function in the `database.py`.

4. Configure your bot token:
    - In `config.py`, add your Telegram bot token:
    ```python
    API_TOKEN = 'your-telegram-bot-token'
    ```

5. Run the bot:
    ```bash
    python bot.py
    ```

### Usage

Once the bot is running, users can start interacting with it using the commands listed above. The bot will store study hours and points in the SQLite database, generate daily and monthly reports, and manage user scores.

## Database Structure

- **Users**: Stores user information (ID, username, total study hours).
- **Study Hours**: Logs the daily study hours of users.
- **Points Awards**: Tracks the points awarded to users.


