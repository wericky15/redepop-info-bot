# === REDE POP BOT 13.0 FINAL COMPLETO ===

import os
import threading
import time
import sqlite3
from datetime import datetime

from flask import Flask
import telebot
from telebot import types

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8586126783
ADMIN_LINK = "https://t.me/Whsantosz"
BASE_LINK = "https://11poptig.com/?pid=1403904093"

bot = telebot.TeleBot(BOT_TOKEN)

# ===== IMAGENS =====
IMG_LANCAMENTO = "https://i.postimg.cc/vHktD7NC/IMG-20260418-215448-769.jpg"
IMG_INDICACAO = "https://i.postimg.cc/bw0S8Qcy/IMG-20260419-034225-247.jpg"
IMG_SALARIO = "https://i.postimg.cc/Zny0QNx4/IMG-20260419-034227-151.jpg"

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

def marcar_lead(uid):
    cursor.execute("UPDATE users SET lead=1 WHERE user_id=?", (uid,))
    conn.commit()

def marcar_afiliado(uid):
    cursor.execute("UPDATE users SET afiliado=1 WHERE user_id=?", (uid,))
    conn.commit()

def gerar_link(uid):
    return f"{BASE_LINK}&user={uid}"

def botoes(uid):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎰 Entrar na POPTIG", callback_data="entrar"))
    kb.add(types.InlineKeyboardButton("💬 Falar com agente", url=ADMIN_LINK))
    return kb

def menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎯 Quero bônus VIP", callback_data="vip"))
    kb.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    kb.add(types.InlineKeyboardButton("👥 Indicar amigos", callback_data="indicar"))
    kb.add(types.InlineKeyboardButton("💰 Salário semanal", callback_data="salario"))
    return kb

# ===== ALERTA =====
def alerta(user):
    username = f"@{user.username}" if user.username else "Sem username"

    bot.send_message(
        ADMIN_ID,
        f"🔥 NOVO LEAD\n\n"
        f"👤 {user.first_name}\n"
        f"🔗 {username}\n"
        f"🆔 {user.id}\n"
        f"👉 tg://user?id={user.id}"
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
        "🔥 *LANÇAMENTO OFICIAL POPTIG* 🔥\n\n"
        "📅 20 de Abril\n\n"
        "💰 Depósito mínimo: R$10\n"
        "💸 Saque mínimo: R$20\n\n"
        "🎁 BENEFÍCIOS:\n"
        "• Bônus de novo membro\n"
        "• Salário semanal\n"
        "• Bônus por indicação\n"
        "• Extras para agentes\n\n"
        "⚡ Quem entra no início sai na frente!",
        parse_mode="Markdown",
        reply_markup=menu()
    )

    threading.Thread(target=funil, args=(user.id,)).start()

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id
    user = c.from_user

    if c.data == "entrar":
        marcar_lead(uid)
        alerta(user)

        bot.send_message(
            uid,
            "🔥 Clique abaixo para acessar a plataforma:",
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
            "3️⃣ Receba estratégia VIP",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    elif c.data == "info":
        bot.send_message(
            uid,
            "ℹ️ *SOBRE A POPTIG*\n\n"
            "💰 Plataforma com ganhos reais\n"
            "👥 Sistema de indicação ativo\n\n"
            "📊 Depósito mínimo: R$10\n"
            "📊 Saque mínimo: R$20",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    elif c.data == "indicar":
        marcar_afiliado(uid)

        bot.send_photo(
            uid,
            IMG_INDICACAO,
            caption=
            "👥 *BÔNUS POR INDICAÇÃO POPTIG* 👥\n\n"
            "🎁 Indique e desbloqueie os baús da TIG\n\n"
            "💰 Valores:\n"
            "• Primeiro baú: R$25\n"
            "• 2 a 50: R$15 cada\n"
            "• 51 a 1000: R$20 cada\n"
            "• 1000+: R$25 cada\n\n"
            "📋 Requisitos:\n"
            "• Depósito acima de R$20\n"
            "• Giro acima de R$200\n\n"
            "🚀 Quanto mais indicar, mais ganha!",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    elif c.data == "salario":
        bot.send_photo(
            uid,
            IMG_SALARIO,
            caption=
            "💰 *SALÁRIO SEMANAL POPTIG* 💰\n\n"
            "📊 Metas:\n"
            "5 = R$50\n"
            "10 = R$100\n"
            "20 = R$200\n"
            "50 = R$500\n"
            "100 = R$1000\n"
            "500 = R$5000\n"
            "1000 = R$10000\n\n"
            "💸 Pagamento toda segunda\n"
            "❌ Sem rollover",
            parse_mode="Markdown",
            reply_markup=botoes(uid)
        )

    # ===== BOTÃO RESPONDER =====
    elif c.data.startswith("responder_"):
        user_id = int(c.data.split("_")[1])

        msg = bot.send_message(
            ADMIN_ID,
            "✍️ Digite a resposta:"
        )

        bot.register_next_step_handler(msg, enviar_resposta, user_id)

# ===== RECEBER MENSAGEM =====
@bot.message_handler(func=lambda m: True)
def receber(msg):
    if msg.from_user.id == ADMIN_ID:
        return

    user = msg.from_user
    username = f"@{user.username}" if user.username else "Sem username"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "💬 Responder",
            callback_data=f"responder_{user.id}"
        )
    )

    bot.send_message(
        ADMIN_ID,
        f"💬 NOVA MENSAGEM\n\n"
        f"👤 {user.first_name}\n"
        f"🔗 {username}\n"
        f"🆔 {user.id}\n\n"
        f"📩 {msg.text}",
        reply_markup=markup
    )

# ===== ENVIAR RESPOSTA =====
def enviar_resposta(msg, user_id):
    try:
        bot.send_message(user_id, msg.text)
        bot.send_message(ADMIN_ID, "✅ Resposta enviada!")
    except:
        bot.send_message(ADMIN_ID, "❌ Erro ao enviar")

# ===== FUNIL =====
def funil(uid):
    time.sleep(600)
    bot.send_message(uid, "👀 Já entrou na POPTIG?", reply_markup=botoes(uid))

    time.sleep(600)
    bot.send_message(uid, "⚠️ Última chance de entrar no começo!", reply_markup=botoes(uid))

# ===== SERVER =====
app = Flask(__name__)

@app.route("/")
def home():
    return "online"

def run():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
