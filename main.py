# === REDE POP BOT 10.0 FINAL ===

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
            (user.id, user.username, user.first_name,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🎯 Bônus VIP", callback_data="vip"))
    m.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    m.add(types.InlineKeyboardButton("👥 Indicar amigos", callback_data="indicar"))
    m.add(types.InlineKeyboardButton("💰 Salário semanal", callback_data="salario"))
    return m

# ===== ALERTA =====
def alerta_lead(user):
    username = f"@{user.username}" if user.username else "Sem username"
    link_user = f"tg://user?id={user.id}"

    bot.send_message(
        ADMIN_ID,
        f"🔥 NOVO LEAD!\n\n"
        f"👤 Nome: {user.first_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: {user.id}\n\n"
        f"👉 Abrir perfil:\n{link_user}"
    )

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    user = msg.from_user
    salvar_usuario(user)

    bot.send_photo(
        user.id,
        IMG_LANCAMENTO,
        caption=
        "🔥 *BEM-VINDO À REDE POP (POPTIG)* 🔥\n\n"
        "📅 Lançamento: 20 de Abril\n"
        "💰 Depósito mínimo: R$10\n"
        "💸 Saque mínimo: R$20\n\n"
        "🎁 Benefícios:\n"
        "• Bônus de entrada\n"
        "• Salário semanal\n"
        "• Indicação premiada\n"
        "• Estratégia VIP\n\n"
        "⚡ Quem entra cedo sai na frente!",
        parse_mode="Markdown",
        reply_markup=menu()
    )

    threading.Thread(target=funil, args=(user.id,)).start()

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    user = c.from_user
    uid = user.id

    if c.data == "click_entrar":
        marcar_lead(uid)
        alerta_lead(user)

        bot.send_message(
            uid,
            "🔥 *Você está a um passo de começar!*\n\nClique abaixo:",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🎰 ACESSAR POPTIG", url=gerar_link(uid))
            )
        )

    elif c.data == "vip":
        bot.send_message(
            uid,
            "🎯 *BÔNUS VIP LIBERADO*\n\n"
            "1️⃣ Crie sua conta\n"
            "2️⃣ Me chama no privado\n"
            "3️⃣ Receba estratégia\n\n"
            "💰 Já tem gente lucrando!",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    elif c.data == "info":
        bot.send_message(
            uid,
            "ℹ️ *COMO FUNCIONA*\n\n"
            "💰 Ganhos jogando\n"
            "👥 Ganhos indicando\n\n"
            "📊 Depósito: R$10\n"
            "📊 Saque: R$20\n\n"
            "🔥 Plataforma nova = oportunidade",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    elif c.data == "indicar":
        marcar_afiliado(uid)

        bot.send_photo(
            uid,
            IMG_INDICACAO,
            caption=
            "👥 *GANHE COM INDICAÇÃO*\n\n"
            "💰 Até R$25 por pessoa\n\n"
            "📋 Requisitos:\n"
            "• Depósito mínimo R$20\n"
            "• Giro mínimo R$200\n\n"
            "🚀 Quanto mais você chama, mais ganha!",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    elif c.data == "salario":
        bot.send_photo(
            uid,
            IMG_SALARIO,
            caption=
            "💰 *SALÁRIO SEMANAL*\n\n"
            "🎯 5 pessoas = R$50\n"
            "🎯 50 pessoas = R$500\n"
            "🎯 100 pessoas = R$1000\n\n"
            "💸 Pagamento toda segunda\n"
            "❌ Sem rollover",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

# ===== FUNIL (2 MENSAGENS) =====
def funil(user_id):
    try:
        time.sleep(600)

        bot.send_message(
            user_id,
            "👀 Já garantiu sua vaga?\n\n🔥 O lançamento já começou",
            reply_markup=botoes(user_id)
        )

        time.sleep(600)

        bot.send_message(
            user_id,
            "⚠️ Último aviso:\n\n🔥 Agora é o melhor momento pra entrar",
            reply_markup=botoes(user_id)
        )

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
