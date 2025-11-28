import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database import get_quiz_index, update_quiz_index, save_quiz_result, get_user_stats, get_global_stats, update_score
from quiz_data import quiz_data
from keyboards import get_main_keyboard, generate_options_keyboard
from utils import get_question, new_quiz, calculate_final_score

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в квиз по САМЫМ ТРУДНЫМ ЗАГАДКАМ! 🐍\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

async def show_user_stats(message: types.Message):
    stats = await get_user_stats(message.from_user.id)
    if stats:
        score, total, completed_at = stats
        await message.answer(
            f"📊 Ваша статистика:\n"
            f"Последний результат: {score}/{total}\n"
            f"Процент правильных: {score/total*100:.1f}%\n"
            f"Завершено: {completed_at}"
        )
    else:
        await message.answer("У вас еще нет результатов квиза. Начните игру!")

async def show_global_stats(message: types.Message):
    stats = await get_global_stats()
    if stats:
        response = "🏆 Топ-10 игроков:\n\n"
        for i, (username, score, total, completed_at) in enumerate(stats, 1):
            response += f"{i}. {username or 'Аноним'}: {score}/{total} ({score/total*100:.1f}%)\n"
        await message.answer(response)
    else:
        await message.answer("Пока нет статистики игроков.")

async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index, current_score = await get_quiz_index(user_id)
    
    # Увеличиваем счетчик правильных ответов
    new_score = current_score + 1
    await update_score(user_id, new_score)
    
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    await callback.message.answer("✅ Верно!")
    
    # Переход к следующему вопросу
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        # Завершение квиза и сохранение результата
        score, total = await calculate_final_score(user_id)
        await save_quiz_result(user_id, callback.from_user.username, score, total)
        await callback.message.answer(
            f"🎉 Квиз завершен!\n"
            f"Ваш результат: {score}/{total}\n"
            f"Используйте /quiz чтобы начать заново.",
            reply_markup=get_main_keyboard()
        )

async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index, current_score = await get_quiz_index(user_id)
    
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    # Показываем правильный ответ
    question_data = quiz_data[current_question_index]
    correct_answer = question_data['options'][question_data['correct_option']]
    
    await callback.message.answer(f"❌ Неправильно. Правильный ответ: {correct_answer}")
    
    # Переход к следующему вопросу (счетчик не увеличиваем)
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        # Завершение квиза и сохранение результата
        score, total = await calculate_final_score(user_id)
        await save_quiz_result(user_id, callback.from_user.username, score, total)
        await callback.message.answer(
            f"🎉 Квиз завершен!\n"
            f"Ваш результат: {score}/{total}\n"
            f"Используйте /quiz чтобы начать заново.",
            reply_markup=get_main_keyboard()
        )

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_quiz, Command("quiz"))
    dp.message.register(cmd_quiz, F.text == "Начать игру")
    dp.message.register(show_user_stats, F.text == "Моя статистика")
    dp.message.register(show_global_stats, F.text == "Общая статистика")
    dp.callback_query.register(right_answer, F.data == "right_answer")
    dp.callback_query.register(wrong_answer, F.data == "wrong_answer")