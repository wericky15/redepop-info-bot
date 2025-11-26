import os
import threading

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# ========= CONFIG BÁSICA ========= #

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN não encontrado. Defina a variável de ambiente no Render.")

bot = telebot.TeleBot(BOT_TOKEN)

# Seus links
LINK_PLATAFORMA = "https://33popn1.com/?pid=3779132759"    # link da plataforma
LINK_GRUPO_VIP = "https://t.me/werickyredpop"              # grupo VIP
USER_SUPORTE = "Whsantosz"                                 # seu @ sem o @


# ========= FUNÇÕES DE MENU ========= #

def menu_inicial():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎯 Quero bônus e acesso VIP", callback_data="lead_vip")
    )
    markup.row(
        InlineKeyboardButton("ℹ Informações sobre a Rede Pop", callback_data="info")
    )
    markup.row(
        InlineKeyboardButton(
            "👨‍💼 Falar com o Agente Oficial",
            url=f"https://t.me/{USER_SUPORTE}"
        )
    )
    return markup


def menu_conversao():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎯 Entrar na Plataforma", url=LINK_PLATAFORMA)
    )
    markup.row(
        InlineKeyboardButton("👑 Entrar no Grupo VIP", url=LINK_GRUPO_VIP)
    )
    markup.row(
        InlineKeyboardButton(
            "👨‍💼 Falar com o Agente Oficial",
            url=f"https://t.me/{USER_SUPORTE}"
        )
    )
    markup.row(
        InlineKeyboardButton("⬅ Voltar ao início", callback_data="voltar_inicio")
    )
    return markup


# ========= REGISTRO DE LEAD ========= #

def registrar_lead(user):
    username = user.username or ""
    first_name = user.first_name or ""
    user_id = user.id
    print(f"[LEAD] Novo jogador interessado: {first_name} (@{username}) id={user_id}")


# ========= HANDLERS DO BOT ========= #

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    texto = (
        "👋 Olá, tudo bem?\n\n"
        "Sou o *Bot Oficial de Informações da Rede Pop*, gerenciado por "
        "*Wericky DK (Agente Oficial da Rede Pop).* \n\n"
        "Aqui você pode:\n"
        "• Entender como a plataforma funciona\n"
        "• Solicitar orientação profissional\n"
        "• Ter acesso a bônus e grupo VIP com suporte direto\n\n"
        "Selecione uma opção abaixo para continuar 👇"
    )
    bot.send_message(
        message.chat.id,
        texto,
        parse_mode="Markdown",
        reply_markup=menu_inicial()
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data

    if data == "lead_vip":
        # registra lead nos logs
        registrar_lead(call.from_user)

        texto = (
            "🎯 *Acesso a Bônus e Grupo VIP*\n\n"
            "Você demonstrou interesse em receber orientação profissional, "
            "acesso a bônus e participar do grupo VIP.\n\n"
            "Use os botões abaixo para avançar:"
        )
        bot.edit_message_text(
            texto,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=menu_conversao()
        )

    elif data == "info":
        texto = (
            "ℹ *Informações sobre a Rede Pop*\n\n"
            "A Rede Pop é uma plataforma de entretenimento digital com sistema "
            "de bônus, campanhas e diversas oportunidades diárias.\n\n"
            "Para começar com orientação e segurança, utilize as opções abaixo:"
        )
        bot.edit_message_text(
            texto,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=menu_conversao()
        )

    elif data == "voltar_inicio":
        bot.edit_message_text(
            "Selecione uma opção para continuar 👇",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=menu_inicial()
        )


# ========= FLASK + THREAD PARA RENDER ========= #

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Rede Pop Info - OK"

def iniciar_bot():
    print("Iniciando bot Telegram (polling)...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # inicia o bot em uma thread
    t = threading.Thread(target=iniciar_bot, daemon=True)
    t.start()

    # inicia servidor web para o Render
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor Flask rodando na porta {port}...")
    app.run(host="0.0.0.0", port=port)
