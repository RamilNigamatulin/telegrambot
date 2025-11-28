import aiosqlite

DB_NAME = 'quiz_bot.db'

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                         (user_id INTEGER PRIMARY KEY, question_index INTEGER, score INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results 
                         (user_id INTEGER, username TEXT, score INTEGER, total INTEGER, 
                         completed_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index, score FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            results = await cursor.fetchone()
            return results[0] if results else 0, results[1] if results else 0

async def update_quiz_index(user_id, index, score=None):
    async with aiosqlite.connect(DB_NAME) as db:
        if score is not None:
            await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', 
                            (user_id, index, score))
        else:
            await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, COALESCE((SELECT score FROM quiz_state WHERE user_id = ?), 0))', 
                            (user_id, index, user_id))
        await db.commit()

async def update_score(user_id, new_score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET score = ? WHERE user_id = ?', (new_score, user_id))
        await db.commit()

async def save_quiz_result(user_id, username, score, total):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''INSERT INTO quiz_results (user_id, username, score, total) 
                         VALUES (?, ?, ?, ?)''', (user_id, username, score, total))
        await db.commit()

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT score, total, completed_at FROM quiz_results 
                              WHERE user_id = ? ORDER BY completed_at DESC LIMIT 1''', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_global_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT username, score, total, completed_at FROM quiz_results 
                              ORDER BY score DESC LIMIT 10''') as cursor:
            return await cursor.fetchall()
        