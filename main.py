# === REDE POP BOT 5.0 (FINAL) ===

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

BOT_USERNAME = os.environ.get("BOT_USERNAME", "RedePop_Info_bot")

BASE_LINK_POPTIG = "https://11poptig.com/?pid=1403904093"

# imagens (coloca na mesma pasta)
IMG_LANCAMENTO = "lancamento.jpg"
IMG_INDICACAO = "indicacao.jpg"
IMG_SALARIO = "salario.jpg"

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
    return f"{BASE_LINK_POPTIG}&user={user_id}"

def total_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def total_refs(user_id):
    cursor.execute("SELECT COUNT(*) FROM users WHERE ref_by=?", (user_id,))
    return cursor.fetchone()[0]

def botao_link(texto, url):
    return types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(texto, url=url)
    )

# ===== MENU =====
def menu(user_id):
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🎯 Bônus VIP", callback_data="vip"))
    m.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    m.add(types.InlineKeyboardButton("👥 Indicar", callback_data="indicar"))
    m.add(types.InlineKeyboardButton("💰 Salário semanal", callback_data="salario"))
    m.add(types.InlineKeyboardButton("🎰 Entrar na POPTIG", url=gerar_link(user_id)))
    return m

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id

    ref = None
    if len(msg.text.split()) > 1:
        param = msg.text.split()[1]
        if "ref_" in param:
            ref = int(param.replace("ref_", ""))

    salvar_usuario(user_id, ref)

    try:
        bot.send_photo(user_id, open(IMG_LANCAMENTO, "rb"))
    except:
        pass

    bot.send_message(
        user_id,
        "🔥 *LANÇAMENTO POPTIG* 🔥\n\n"
        "💰 Depósito mínimo: R$10\n"
        "💸 Saque: R$20\n\n"
        "🎁 Bônus + VIP + estratégia\n\n"
        "👇 Escolha abaixo:",
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
            "🎯 Bônus liberado!\n\nEntre e me chama pra ativar 👇",
            reply_markup=botao_link("🎰 Entrar", gerar_link(user_id))
        )

    elif c.data == "info":
        bot.send_message(
            user_id,
            "ℹ️ Plataforma com ganhos + indicação\n\nTeste agora 👇",
            reply_markup=botao_link("🔥 Começar", gerar_link(user_id))
        )

    elif c.data == "indicar":
        try:
            bot.send_photo(user_id, open(IMG_INDICACAO, "rb"))
        except:
            pass

        link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

        bot.send_message(
            user_id,
            f"👥 Seu link:\n{link}\n\n💰 Indicados: {total_refs(user_id)}",
            reply_markup=botao_link("🚀 Convidar", link)
        )

    elif c.data == "salario":
        try:
            bot.send_photo(user_id, open(IMG_SALARIO, "rb"))
        except:
            pass

        bot.send_message(
            user_id,
            "💰 Ganhe salário semanal batendo metas!\n\n🔥 Pagamento toda segunda",
            reply_markup=botao_link("🔥 Começar", gerar_link(user_id))
        )

# ===== BROADCAST =====
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.chat.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, "📢 Envie mensagem:")
    bot.register_next_step_handler(msg, send_all)

def send_all(msg):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for u in users:
        try:
            bot.send_message(
                u[0],
                msg.text,
                reply_markup=botao_link("🔥 Entrar na POPTIG", gerar_link(u[0]))
            )
            time.sleep(0.3)
        except:
            pass

# ===== FUNIL =====
def funil(user_id):
    try:
        for texto, botao in [
            ("👀 Já entrou?\n\n🔥 Lançamento rolando", "Entrar"),
            ("💰 Tem gente lucrando...\n\nNão fica de fora", "Começar"),
            ("👥 Ganhe indicando pessoas", "Criar conta"),
            ("💸 Salário semanal disponível", "Ver agora"),
            ("⚠️ Última chance de entrar cedo", "Garantir vaga")
        ]:
            time.sleep(600)
            bot.send_message(
                user_id,
                texto,
                reply_markup=botao_link(botao, gerar_link(user_id))
            )
    except:
        pass

# ===== STATS =====
@bot.message_handler(commands=['stats'])
def stats(msg):
    if msg.chat.id == ADMIN_ID:
        bot.send_message(msg.chat.id, f"👥 Usuários: {total_users()}")

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
