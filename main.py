# === REDE POP BOT 6.0 FINAL ===

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
BOT_USERNAME = "RedePop_Info_bot"  # ⚠️ CONFERE ISSO

ADMIN_LINK = "https://t.me/Whsantosz"
BASE_LINK = "https://11poptig.com/?pid=1403904093"

# 🔥 IMAGENS
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
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, ref_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

def gerar_link(user_id):
    return f"{BASE_LINK}&user={user_id}"

def total_refs(user_id):
    cursor.execute("SELECT COUNT(*) FROM users WHERE ref_by=?", (user_id,))
    return cursor.fetchone()[0]

def botao_principal(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎰 Entrar na POPTIG", url=gerar_link(user_id)))
    markup.add(types.InlineKeyboardButton("💬 Falar com agente", url=ADMIN_LINK))
    return markup

# ===== MENU =====
def menu(user_id):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🎯 Bônus VIP", callback_data="vip"))
    m.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    m.add(types.InlineKeyboardButton("👥 Indicar amigos", callback_data="indicar"))
    m.add(types.InlineKeyboardButton("💰 Salário semanal", callback_data="salario"))
    return m

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id

    ref = None
    if len(msg.text.split()) > 1:
        param = msg.text.split()[1]
        if "ref_" in param:
            try:
                ref = int(param.replace("ref_", ""))
            except:
                pass

    salvar_usuario(user_id, ref)

    bot.send_photo(
        user_id,
        IMG_LANCAMENTO,
        caption=
        "🔥 *LANÇAMENTO POPTIG* 🔥\n\n"
        "💰 Depósito mínimo: R$10\n"
        "💸 Saque mínimo: R$20\n\n"
        "🎁 Bônus + VIP + estratégia\n\n"
        "⚡ Entre agora e saia na frente!",
        parse_mode="Markdown",
        reply_markup=menu(user_id)
    )

    threading.Thread(target=funil, args=(user_id,)).start()

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    user_id = c.from_user.id

    if c.data == "vip":
        bot.send_message(
            user_id,
            "🎯 *BÔNUS VIP LIBERADO*\n\n"
            "🔥 Você entrou no melhor momento\n\n"
            "👉 Cria sua conta e me chama\n"
            "Vou te passar estratégia pra começar forte\n\n"
            "💰 Tem gente já lucrando no início",
            parse_mode="Markdown",
            reply_markup=botao_principal(user_id)
        )

    elif c.data == "info":
        bot.send_message(
            user_id,
            "ℹ️ *COMO FUNCIONA*\n\n"
            "💰 Você ganha jogando\n"
            "👥 Pode ganhar indicando\n\n"
            "📊 Depósito mínimo: R$10\n"
            "📊 Saque mínimo: R$20\n\n"
            "🔥 Plataforma nova = mais oportunidade",
            parse_mode="Markdown",
            reply_markup=botao_principal(user_id)
        )

    elif c.data == "indicar":
        link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

        bot.send_photo(
            user_id,
            IMG_INDICACAO,
            caption=
            "👥 *GANHE INDICANDO*\n\n"
            "💰 Até R$25 por pessoa\n\n"
            "📋 Regras:\n"
            "• Depósito mínimo: R$20\n"
            "• Giro: R$200\n\n"
            f"🔗 Seu link:\n{link}\n\n"
            f"👥 Indicados: {total_refs(user_id)}",
            parse_mode="Markdown",
            reply_markup=botao_principal(user_id)
        )

    elif c.data == "salario":
        bot.send_photo(
            user_id,
            IMG_SALARIO,
            caption=
            "💰 *SALÁRIO SEMANAL*\n\n"
            "🎯 5 pessoas = R$50\n"
            "🎯 50 pessoas = R$500\n"
            "🎯 100 pessoas = R$1000\n\n"
            "💸 Pagamento toda segunda",
            parse_mode="Markdown",
            reply_markup=botao_principal(user_id)
        )

# ===== BROADCAST =====
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "📢 Envie a mensagem:")
    bot.register_next_step_handler(msg, enviar)

def enviar(msg):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for u in users:
        try:
            bot.send_message(
                u[0],
                msg.text,
                reply_markup=botao_principal(u[0])
            )
            time.sleep(0.3)
        except:
            pass

# ===== FUNIL =====
def funil(user_id):
    try:
        textos = [
            "👀 Já entrou na POPTIG?\n\n🔥 Tá no começo ainda",
            "💰 Tem gente se preparando pra lucrar...",
            "👥 Você pode ganhar indicando",
            "💸 Tem salário semanal também",
            "⚠️ Última chance de entrar cedo"
        ]

        for t in textos:
            time.sleep(600)
            bot.send_message(user_id, t, reply_markup=botao_principal(user_id))

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
