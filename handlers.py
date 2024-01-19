# handlers.py
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from telegram.ext import CallbackContext, ContextTypes

from DataBase import DatabaseManager
from Questions import questions
from learning_style_questions import learning_style_questions
from config import admin_user_id

# Create a DatabaseManager instance
db_manager = DatabaseManager()

awaiting_learning_style = {}
awaiting_contact = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db_manager.save_user_data(user_id, datetime.now(), None, None, 0, 0, 0, "AWAITING_NAME")
    await update.message.reply_text(
        "Hi, mate! Давай подивимось у якому стані зараз твоя граматика. Цей тест потрібен лише для того, аби ми могли приблизно оцінити твій рівень, тож ніде не підглядай, відповідай чесно! Свій остаточний висновок із пропозицією групи та рівня навчання ми надішлемо після невеличкого 15 хвилинного інтерв’ю у якому матимемо змогу перевірити рівень спілкування та дізнатись більше інформації:)")  # rest of your message
    keyboard = [[InlineKeyboardButton("Start Test", callback_data='start_test')]]
    await update.message.reply_text('Натисни кнопку "Start test" для початку грамматичного тесту \nВикористовуй активні кнопки для надання відповіді на питання',
                                    reply_markup=InlineKeyboardMarkup(keyboard))


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    current_score = 0
    percentage = 0

    user_data = db_manager.get_user_data(user_id)
    if not user_data:
        await query.answer()
        return

    # If user_data is available, extract current_question from it.
    current_question = user_data[5]

    if query.data == 'start_test':
        # When test starts, set the user state to 'AWAITING_TEST_ANSWERS'
        db_manager.save_user_data(user_id, datetime.now(), user_data[2], user_data[3], current_score, percentage, 0, "AWAITING_TEST_ANSWERS")
        options = questions[0]['options']
        keyboard = [KeyboardButton(option) for option in options]
        await query.message.reply_text(questions[0]['text'],
                                       reply_markup=ReplyKeyboardMarkup([keyboard], one_time_keyboard=True,
                                                                        resize_keyboard=True))

    if query.data == 'start_learning_style_test':
        await start_learning_style_test(update, context)

    if query.data == 'skip_learning_style_test':
        await query.message.reply_text(
            "З нетерпінням чекаємо зустрічі, наша команда вже зовсім скоро з тобою зв'яжеться)")


async def text_message_handler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text
    user_data = db_manager.get_user_data(user_id)

    # Utility functions
    def is_valid_phone_number(phone):
        pattern = re.compile(r"^\+?\d{9,15}$")
        return pattern.match(phone)

    def normalize_phone_number(phone):
        return re.sub(r"[^\d]", '', phone)

    if not user_data:
        await update.message.reply_text("Sorry, I couldn't fetch your data. Please start the test again.")
        return

    current_state = user_data[7]  # Changed from user_data[6] to user_data[7] as state is the 8th element in the tuple
    current_score = user_data[4]
    current_question = user_data[6]
    percentage = user_data[5]

    if current_state == "AWAITING_TEST_ANSWERS":
        correct_answer = questions[current_question]["answer"]
        print(f"Expected: {correct_answer}, Received: {user_input}")
        if correct_answer == user_input:
            current_score += 1
        percentage = (current_score / (
                    current_question + 1)) * 100  # Adjust the denominator for the percentage calculation
        current_question += 1
        if current_question < len(questions):
            percentage = (current_score / current_question) * 100
            db_manager.save_user_data(user_id, datetime.now(), user_data[2], user_data[3], current_score, percentage,
                                      current_question, "AWAITING_TEST_ANSWERS")

            options = questions[current_question]['options']
            keyboard = [[KeyboardButton(option) for option in options]]
            await update.message.reply_text(text=questions[current_question]['text'],
                                            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                             resize_keyboard=True))
        else:
            percentage = (current_score / len(questions)) * 100
            db_manager.save_user_data(user_id, datetime.now(), user_data[2], user_data[3], current_score, percentage,
                                      current_question, "AWAITING_NAME")
            await update.message.reply_text(
                f"Супер! Наша команда отримала результати твого граматичного тесту! Good job, mate!",
                reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text("Вкажи як було б ліпше нам до тебе звертатися")


    elif current_state == "AWAITING_NAME":
        user_name = user_input.strip()  # remove any leading or trailing spaces
        if user_name:  # Check if the user has actually provided a non-empty name
            db_manager.save_user_data(user_id, datetime.now(), user_name, user_data[3], current_score, percentage,
                                      current_question, "AWAITING_PHONE")
            await update.message.reply_text(f"Дякую {user_name}! Тепер вкажи твій номер телефону:")
        else:
            await update.message.reply_text("Здаєтся ти нічого не ввів")

    elif current_state == "AWAITING_PHONE":
        if is_valid_phone_number(user_input):
            normalized_phone = normalize_phone_number(user_input)
            db_manager.save_user_data(user_id, datetime.now(), user_data[2], normalized_phone, current_score,
                                      percentage, current_question, "AWAITING_LEARNING_STYLE_CHOICE")
            # Offer to take the learning style test after providing contact information
            keyboard = [
                [InlineKeyboardButton("Вже біжу відповідати", callback_data='start_learning_style_test')],

                [InlineKeyboardButton("Відповім пізніше", callback_data='skip_learning_style_test')]
            ]
            await update.message.reply_text(
                'Час познайомитись ближче! Ми б хотіли дізнатись трішки більше про твої вподобаннята та бажання. Звісно, під час наших уроків ми будемо читати, писати, спілкуватись та робити інтерактивні вправи. Але щоб зробити ці уроки комфортними, нам потрібно дізнатись приблизний стиль твого навчання та зробити певні висновки у вигляді подальшої стратегії:))',
                reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("Хмм...Номер телефону що ти ввів не є дійсним, спробуй ще раз.")


    elif user_id in awaiting_learning_style:  # Checking if the user is in the middle of the learning style test
        awaiting_learning_style[user_id].append(user_input)
        total_answers = len(awaiting_learning_style[user_id])
        if total_answers < len(learning_style_questions):
            # Prompt next question
            options = learning_style_questions[total_answers]['options']
            keyboard = [[KeyboardButton(option) for option in options]]
            await update.message.reply_text(text=learning_style_questions[total_answers]['text'],
                                            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                             resize_keyboard=True))
        else:
            # Calculate and store learning style percentages
            answers = awaiting_learning_style[user_id]
            percentages = calculate_learning_style_percentages(answers)
            db_manager.save_user_data(user_id, user_data[1], user_data[2], user_data[3], user_data[4], user_data[5],
                                      user_data[6], user_data[7], total_answers,
                                      percentages['V'], percentages['A'], percentages['R'], percentages['K'])
            # Inform user and clear their awaiting state
            del awaiting_learning_style[user_id]
            await update.message.reply_text("Дякуємо за таку важливу інформацію! З нетерпінням чекаємо зустрічі, наша команда вже зовсім скоро з тобою зв'яжеться)")


async def start_learning_style_test(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id  # Use callback_query here
    awaiting_learning_style[user_id] = []
    options = learning_style_questions[0]['options']
    keyboard = [[KeyboardButton(option) for option in options]]
    await update.callback_query.message.reply_text(learning_style_questions[0]['text'],
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
async def help_command(update: Update, context: CallbackContext):
    help_text = f"Need help? [Contact our Administrator](https://t.me/{admin_user_id})"
    await update.message.reply_text(help_text, parse_mode='Markdown')


def calculate_learning_style_percentages(answers: list) -> dict:
    v_count = answers.count("V")
    a_count = answers.count("A")
    r_count = answers.count("R")
    k_count = answers.count("K")

    total_count = len(answers)

    v_percent = (v_count / total_count) * 100
    a_percent = (a_count / total_count) * 100
    r_percent = (r_count / total_count) * 100
    k_percent = (k_count / total_count) * 100

    return {
        "V": v_percent,
        "A": a_percent,
        "R": r_percent,
        "K": k_percent
    }