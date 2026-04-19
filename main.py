# === REDE POP BOT 8.0 FINAL (LEADS + ALERTA) ===

import os
import threading
import time
import sqlite3
from datetime import datetime

from flask import Flask
import telebot
from telebot import types

# ===== CONFIG =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8586126783
ADMIN_LINK = "https://t.me/Whsantosz"
BASE_LINK = "https://11poptig.com/?pid=1403904093"

# IMAGENS
IMG_LANCAMENTO = "https://i.postimg.cc/vHktD7NC/IMG-20260418-215448-769.jpg"
IMG_INDICACAO = "https://i.postimg.cc/bw0S8Qcy/IMG-20260419-034225-247.jpg"
IMG_SALARIO = "https://i.postimg.cc/Zny0QNx4/IMG-20260419-034227-151.jpg"

bot = telebot.TeleBot(BOT_TOKEN)

# ===== DATABASE =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    date TEXT,
    lead INTEGER DEFAULT 0,
    afiliado INTEGER DEFAULT 0
)
""")
conn.commit()

# ===== FUNÇÕES =====
def salvar_usuario(user):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, 0, 0)",
            (
                user.id,
                user.username,
                user.first_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        conn.commit()

def marcar_lead(user_id):
    cursor.execute("UPDATE users SET lead=1 WHERE user_id=?", (user_id,))
    conn.commit()

def marcar_afiliado(user_id):
    cursor.execute("UPDATE users SET afiliado=1 WHERE user_id=?", (user_id,))
    conn.commit()

def gerar_link(user_id):
    return f"{BASE_LINK}&user={user_id}"

def botoes(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎰 Entrar na POPTIG", callback_data="click_entrar"))
    markup.add(types.InlineKeyboardButton("💬 Falar com agente", url=ADMIN_LINK))
    return markup

def menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎯 Bônus VIP", callback_data="vip"))
    markup.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    markup.add(types.InlineKeyboardButton("👥 Indicar amigos", callback_data="indicar"))
    markup.add(types.InlineKeyboardButton("💰 Salário semanal", callback_data="salario"))
    return markup

# ===== ALERTA =====
def alerta_lead(user):
    try:
        username = f"@{user.username}" if user.username else "Sem username"

        bot.send_message(
            ADMIN_ID,
            f"🔥 NOVO LEAD!\n\n"
            f"👤 Nome: {user.first_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 ID: {user.id}\n\n"
            f"💰 Clicou em ENTRAR"
        )
    except:
        pass

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    user = msg.from_user
    salvar_usuario(user)

    bot.send_photo(
        user.id,
        IMG_LANCAMENTO,
        caption=
        "🔥 *LANÇAMENTO POPTIG* 🔥\n\n"
        "💰 Depósito mínimo: R$10\n"
        "💸 Saque mínimo: R$20\n\n"
        "🎁 Bônus + VIP + estratégia\n\n"
        "⚡ Entre agora e saia na frente!",
        parse_mode="Markdown",
        reply_markup=menu()
    )

    threading.Thread(target=funil, args=(user.id,)).start()

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    user = c.from_user
    user_id = user.id

    if c.data == "click_entrar":
        marcar_lead(user_id)
        alerta_lead(user)

        bot.send_message(
            user_id,
            "🔥 Boa escolha!\n\nClique abaixo:",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🎰 ACESSAR POPTIG", url=gerar_link(user_id))
            )
        )

    elif c.data == "vip":
        bot.send_message(
            user_id,
            "🎯 *BÔNUS VIP*\n\nCria a conta e me chama que te ajudo!",
            parse_mode="Markdown",
            reply_markup=botoes(user_id)
        )

    elif c.data == "info":
        bot.send_message(
            user_id,
            "ℹ️ Depósito: R$10\nSaque: R$20\n\nGanhe jogando e indicando!",
            reply_markup=botoes(user_id)
        )

    elif c.data == "indicar":
        marcar_afiliado(user_id)

        bot.send_photo(
            user_id,
            IMG_INDICACAO,
            caption=
            "👥 Ganhe até R$25 por indicação!\n\n"
            "Requisitos:\nDepósito R$20\nGiro R$200",
            reply_markup=botoes(user_id)
        )

    elif c.data == "salario":
        bot.send_photo(
            user_id,
            IMG_SALARIO,
            caption=
            "💰 Salário semanal!\n\n5 pessoas = R$50\n50 = R$500\n100 = R$1000",
            reply_markup=botoes(user_id)
        )

# ===== COMANDO LEADS =====
@bot.message_handler(commands=['leads'])
def leads(msg):
    if msg.chat.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE lead=1")
    leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE afiliado=1")
    afiliados = cursor.fetchone()[0]

    bot.send_message(
        msg.chat.id,
        f"👥 Total: {total}\n🔥 Leads: {leads}\n💰 Afiliados: {afiliados}"
    )

# ===== FUNIL =====
def funil(user_id):
    try:
        msgs = [
            "👀 Já entrou?",
            "💰 Tá no começo...",
            "👥 Dá pra indicar",
            "💸 Tem salário",
            "⚠️ Última chance"
        ]

        for m in msgs:
            time.sleep(600)
            bot.send_message(user_id, m, reply_markup=botoes(user_id))

    except:
        pass

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "online"

def run():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
