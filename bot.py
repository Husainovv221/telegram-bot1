import asyncio
import sqlite3
import time
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputMediaPhoto
)

logging.basicConfig(level=logging.INFO)

TOKEN = "8963873427:AAENbfXI02XktRL6YwMZDrWpeAexWvAPPRk"
ADMIN_ID = 7457739417

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =======================
# 📦 SQLITE
# =======================
conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    username TEXT,
    product TEXT,
    user_id INTEGER,
    status TEXT
)
""")

conn.commit()

# =======================
# 📋 ДАННЫЕ
# =======================
user_step = {}
user_data = {}
table_step = {}
cart = {}
last_message = {}

# =======================
# 📋 МЕНЮ
# =======================
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📏 Высокие столы")],
        [KeyboardButton(text="📉 Низкие столы")],
        [KeyboardButton(text="🛒 Корзина")],
        [KeyboardButton(text="📦 Мои заказы")]
    ],
    resize_keyboard=True
)

high_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇹🇷 Турецкие")],
        [KeyboardButton(text="🪵 Лофт")],
        [KeyboardButton(text="🪞 Консоль")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

# =======================
# 📸 ФОТО
# =======================
turkish_media = [
    InputMediaPhoto(media="https://i.postimg.cc/kXN9hwhM/6207b052-d560-45e8-bc85-917338a17982.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/JzfwYDCW/8a44e245-29ed-402d-8163-ff9b4a101903.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/HLwNS6tx/7f5e2e30-0662-40dc-96c1-414dbb4577d0.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/CLRQyhNY/f95a1c99-32dc-41af-a390-317731f04d8f.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/fyJBhCY0/1f8ae59b-a4c8-4c61-b511-f61455e01b97.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/FKpZd8Zz/32808f4b-990c-438b-8555-5f6877d0fa5c.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/GhD683sm/2c1f5727-754d-49ca-b029-6fbb6e6bd8f5.jpg"),
    InputMediaPhoto(media="https://i.postimg.cc/ZRgDnXb1/4f0dcf41-57f4-4bbe-a641-d571402208d4.jpg"),
]

def catalog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪑 Эльф"), KeyboardButton(text="🪑 Роза")],
            [KeyboardButton(text="🪑 Каталог"), KeyboardButton(text="🪑 Турция")],
            [KeyboardButton(text="🪑 Sima"), KeyboardButton(text="🪑 Элит")],
            [KeyboardButton(text="🪑 Адем"), KeyboardButton(text="🪑 Бохем")],
            [KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

# =======================
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Добро пожаловать!", reply_markup=menu)

# =======================
@dp.message()
async def handler(message: Message):

    try:
        user_id = message.from_user.id
        text = message.text

        now = time.time()
        if user_id in last_message and now - last_message[user_id] < 0.8:
            return
        last_message[user_id] = now

        # reset
        if text in ["📏 Высокие столы","📉 Низкие столы","🇹🇷 Турецкие"]:
            user_step[user_id] = None

        if text == "⬅️ Назад":
            user_step[user_id] = None
            user_data[user_id] = {}
            await message.answer("🔙 Главное меню", reply_markup=menu)
            return

        if text in ["📏 Высокие столы","📉 Низкие столы"]:
            await message.answer("Выбери тип 👇", reply_markup=high_menu)
            return

        if text == "🇹🇷 Турецкие":
            await message.answer_media_group(turkish_media)
            await message.answer("👇 Выбери стол:", reply_markup=catalog_keyboard())
            return

        if text in ["🪑 Эльф","🪑 Роза","🪑 Каталог","🪑 Турция","🪑 Sima","🪑 Элит","🪑 Адем","🪑 Бохем"]:
            table_step[user_id] = text
            await message.answer(
                f"Вы выбрали: {text}",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="🛒 Добавить в корзину")],
                        [KeyboardButton(text="📦 Заказать сейчас")],
                        [KeyboardButton(text="⬅️ Назад")]
                    ],
                    resize_keyboard=True
                )
            )
            return

        # =======================
        # 🛒 КОРЗИНА
        # =======================
        if text == "🛒 Добавить в корзину":
            product = table_step.get(user_id)
            if product:
                cart.setdefault(user_id, []).append(product)
                await message.answer("Добавлено в корзину")
            return

        if text == "🛒 Корзина":
            items = cart.get(user_id, [])
            if not items:
                await message.answer("Корзина пустая")
                return

            await message.answer(
                "🛒 Корзина:\n" + "\n".join(items),
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="✅ Оформить корзину")],
                        [KeyboardButton(text="❌ Очистить корзину")],
                        [KeyboardButton(text="⬅️ Назад")]
                    ],
                    resize_keyboard=True
                )
            )
            return

        if text == "❌ Очистить корзину":
            cart[user_id] = []
            await message.answer("Корзина очищена", reply_markup=menu)
            return

        # =======================
        # 📦 ЗАКАЗ
        # =======================
        if text == "📦 Заказать сейчас":
            product = table_step.get(user_id)

            if product:
                cart.setdefault(user_id, []).append(product)

            if not cart.get(user_id):
                await message.answer("Корзина пустая")
                return

            user_step[user_id] = "name"
            user_data[user_id] = {}
            await message.answer("✍️ Напиши своё имя:")
            return

        if text == "✅ Оформить корзину":
            if not cart.get(user_id):
                await message.answer("Корзина пустая")
                return

            user_step[user_id] = "name"
            user_data[user_id] = {}
            await message.answer("✍️ Напиши своё имя:")
            return

        # =======================
        # 🧠 ШАГИ
        # =======================
        if user_step.get(user_id) == "name":
            user_data[user_id]["name"] = text
            user_step[user_id] = "phone"
            await message.answer("📞 Теперь номер:")
            return

        if user_step.get(user_id) == "phone":
            user_data[user_id]["phone"] = text
            user_step[user_id] = None

            items = cart.get(user_id, [])

            cursor.execute("""
                INSERT INTO orders (name, phone, username, product, user_id, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_data[user_id]["name"],
                user_data[user_id]["phone"],
                message.from_user.username or "нет",
                ", ".join(items),
                user_id,
                "Новый"
            ))

            conn.commit()
            cart[user_id] = []

            # =======================
            # 📦 МОИ ЗАКАЗЫ (FIX)
            # =======================
            await message.answer("Заказ оформлен!", reply_markup=menu)
            return

        # =======================
        # 📦 МОИ ЗАКАЗЫ (ИСПРАВЛЕНО)
        # =======================
        if text == "📦 Мои заказы":

            cursor.execute("""
                SELECT product, status
                FROM orders
                WHERE user_id = ?
                ORDER BY id DESC
            """, (user_id,))

            orders = cursor.fetchall()

            if not orders:
                await message.answer("📭 У тебя пока нет заказов")
                return

            result = "📦 Твои заказы:\n\n"

            for product, status in orders:
                if status is None:
                    status = "Новый"
                result += f"🪑 {product}\n📊 {status}\n\n"

            await message.answer(result)
            return

    except Exception as e:
        print("ERROR:", e)
        await message.answer("Ошибка")

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
