from aiogram import types
from quiz_data import quiz_data
from database import get_quiz_index, update_quiz_index, save_quiz_result, update_score
from keyboards import generate_options_keyboard

async def get_question(message, user_id):
    current_question_index, current_score = await get_quiz_index(user_id)
    if current_question_index < len(quiz_data):
        question_data = quiz_data[current_question_index]
        correct_index = question_data['correct_option']
        opts = question_data['options']
        kb = generate_options_keyboard(opts, opts[correct_index])
        await message.answer(f"Вопрос {current_question_index + 1}/{len(quiz_data)}:\n\n{question_data['question']}", 
                           reply_markup=kb)
    else:
        await message.answer("Квиз завершен! Используйте /quiz чтобы начать заново.")

async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0, 0)  # Сбрасываем и индекс и счетчик
    await get_question(message, user_id)

async def calculate_final_score(user_id):
    current_question_index, current_score = await get_quiz_index(user_id)
    return current_score, len(quiz_data)