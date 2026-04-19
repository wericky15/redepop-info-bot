# === REDE POP INFO BOT 3.5 (POPTIG) ===
# Wericky DK - Agente da Rede Pop

import os
import threading
import time
from datetime import datetime, timedelta

from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8586126783

BANNER_PATH = "banner.png"

# 🔥 LINK POPTIG (ATUALIZADO)
BASE_LINK_POPTIG = "https://11poptig.com/?pid=1403904093"

GROUP_VIP_LINK = "https://t.me/werickyredpop"
BOT_USERNAME = os.environ.get("BOT_USERNAME", "RedePop_Info_bot")

bot = telebot.TeleBot(BOT_TOKEN)

# ===== FUNÇÃO LINK =====
def gerar_link_poptig(user_id=None, origem="default"):
    if user_id:
        return (
            f"{BASE_LINK_POPTIG}"
            f"&utm_source=bot"
            f"&utm_campaign={origem}"
            f"&user={user_id}"
        )
    return BASE_LINK_POPTIG

# ===== MENU =====
def criar_menu(user_id):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("🎯 Quero bônus VIP", callback_data="lead"))
    markup.add(types.InlineKeyboardButton("ℹ️ Informações", callback_data="info"))
    markup.add(types.InlineKeyboardButton("👥 Indicar amigos", callback_data="indicar"))
    markup.add(types.InlineKeyboardButton("👨‍💼 Falar com o agente", url=f"tg://user?id={ADMIN_ID}"))
    markup.add(types.InlineKeyboardButton("🎰 Jogar na POPTIG", url=gerar_link_poptig(user_id)))

    return markup

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        with open(BANNER_PATH, "rb") as banner:
            bot.send_photo(chat_id, banner)
    except:
        pass

    bot.send_message(
        chat_id,
        "🔥 *Bem-vindo à Rede Pop (POPTIG)* 🔥\n\n"
        "Aqui você entra com bônus, suporte VIP e estratégia.\n\n"
        "👇 Escolha abaixo:",
        parse_mode="Markdown",
        reply_markup=criar_menu(user_id)
    )

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call.data == "lead":
        bot.send_message(
            chat_id,
            "🎯 *Bônus VIP liberado!*\n\n"
            "🔥 Entre agora na POPTIG e fale comigo no VIP pra ativar seu bônus 👇",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🎰 Jogar na POPTIG", url=gerar_link_poptig(user_id))
            )
        )

        # mensagem no PV
        bot.send_message(
            user_id,
            "👋 Fala! Aqui é o Wericky DK.\n\n"
            "Me chama e fala quanto quer investir que eu te ajudo a começar na POPTIG 🔥"
        )

    elif call.data == "info":
        bot.send_message(
            chat_id,
            "ℹ️ *Sobre a POPTIG*\n\n"
            "Plataforma da Rede Pop com bônus e jogos rápidos.\n\n"
            "💥 Quer testar agora?\nClique abaixo 👇",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🎰 Jogar agora na POPTIG", url=gerar_link_poptig(user_id))
            )
        )

    elif call.data == "indicar":
        link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

        bot.send_message(
            user_id,
            f"👥 Seu link de indicação:\n\n{link}\n\n"
            "Manda pros amigos e chama eles pra Rede Pop 🔥"
        )

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando!"

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
