# === REDE POP BOT 4.0 (POPTIG) ===
# Wericky DK

import os
import threading
import time
import sqlite3
from datetime import datetime

from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8586126783

BASE_LINK_POPTIG = "https://11poptig.com/?pid=1403904093"
GROUP_VIP_LINK = "https://t.me/werickyredpop"
BOT_USERNAME = os.environ.get("BOT_USERNAME", "RedePop_Info_bot")

bot = telebot.TeleBot(BOT_TOKEN)

# ===== DATABASE =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ref_by INTEGER,
    date TEXT
)
""")

conn.commit()

# ===== FUNÇÕES =====
def salvar_usuario(user_id, ref_by=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (user_id, ref_by, date) VALUES (?, ?, ?)",
            (user_id, ref_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

def total_usuarios():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def total_indicados(user_id):
    cursor.execute("SELECT COUNT(*) FROM users WHERE ref_by=?", (user_id,))
    return cursor.fetchone()[0]

def gerar_link_poptig(user_id=None, origem="bot"):
    return f"{BASE_LINK_POPTIG}&utm_source=bot&utm_campaign={origem}&user={user_id}"

# ===== MENU =====
def menu(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎯 Quero bônus VIP", callback_data="lead"))
    markup.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    markup.add(types.InlineKeyboardButton("👥 Indicar amigos", callback_data="indicar"))
    markup.add(types.InlineKeyboardButton("👨‍💼 Falar com agente", url=f"tg://user?id={ADMIN_ID}"))
    markup.add(types.InlineKeyboardButton("🎰 Jogar na POPTIG", url=gerar_link_poptig(user_id)))
    return markup

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    ref_by = None
    if len(message.text.split()) > 1:
        ref = message.text.split()[1]
        if "ref_" in ref:
            ref_by = int(ref.replace("ref_", ""))

    salvar_usuario(user_id, ref_by)

    bot.send_message(
        chat_id,
        "🔥 *Bem-vindo à Rede Pop (POPTIG)* 🔥\n\n"
        "Ganhe bônus + acesso VIP + estratégia.\n\n👇 Escolha abaixo:",
        parse_mode="Markdown",
        reply_markup=menu(user_id)
    )

    # follow-up automático
    threading.Thread(target=funil_automatico, args=(user_id,)).start()

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call.data == "lead":
        bot.send_message(
            chat_id,
            "🎯 *Bônus VIP liberado!*\n\n"
            "Entre agora e me chama pra ativar 🔥",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🎰 Jogar agora", url=gerar_link_poptig(user_id))
            )
        )

    elif call.data == "info":
        bot.send_message(
            chat_id,
            "ℹ️ Plataforma com jogos rápidos + bônus.\n\nTeste agora 👇",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🎰 Jogar", url=gerar_link_poptig(user_id))
            )
        )

    elif call.data == "indicar":
        link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
        indicados = total_indicados(user_id)

        bot.send_message(
            chat_id,
            f"👥 Seu link:\n{link}\n\n🔥 Indicados: {indicados}"
        )

# ===== BROADCAST =====
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "📢 Envie a mensagem:")
    bot.register_next_step_handler(msg, enviar_broadcast)

def enviar_broadcast(msg):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    enviados = 0

    for user in users:
        try:
            bot.send_message(user[0], msg.text)
            enviados += 1
            time.sleep(0.3)
        except:
            pass

    bot.send_message(msg.chat.id, f"✅ Enviado para {enviados} usuários!")

# ===== STATS =====
@bot.message_handler(commands=['stats'])
def stats(msg):
    if msg.chat.id != ADMIN_ID:
        return

    bot.send_message(
        msg.chat.id,
        f"📊 Usuários: {total_usuarios()}"
    )

# ===== FUNIL AUTOMÁTICO =====
def funil_automatico(user_id):
    time.sleep(60)

    try:
        bot.send_message(
            user_id,
            "🔥 Já entrou na POPTIG?\n\nHoje tem bônus liberado!"
        )

        time.sleep(120)

        bot.send_message(
            user_id,
            "💰 Tem gente sacando todos os dias...\n\nNão fica de fora 👇"
        )

    except:
        pass

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot online!"

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
