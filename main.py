# === REDE POP INFO BOT 2.0 ===
# Wericky DK - Agente da Rede Pop

import os
import threading
from datetime import datetime

from flask import Flask
import telebot
from telebot import types

# ===== CONFIGURAÇÕES BÁSICAS =====

# Token do bot (vem das variáveis de ambiente do Render)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Seu ID para receber os leads
ADMIN_ID = 8586126783  # Wericky DK

# Nome do arquivo do banner que você renomeou no GitHub
BANNER_PATH = "banner.png"

# Link da plataforma POPVAI
LINK_POPVAI = "https://11popvai.com/?pid=3291819190"

# Link do seu contato / grupo
LINK_CONTATO = "https://t.me/werickyredpop"

bot = telebot.TeleBot(BOT_TOKEN)


# ===== FUNÇÃO PARA REGISTRAR LEAD =====

def registrar_lead(user):
    nome = user.first_name or "Sem nome"
    username = user.username or "sem_username"
    user_id = user.id
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Mensagem para você (admin)
    texto = (
        "📥 *NOVO LEAD REDE POP*\n\n"
        f"👤 *Nome:* {nome}\n"
        f"📛 *Username:* @{username}\n"
        f"🆔 *ID:* `{user_id}`\n"
        f"⏰ *Data e horário:* {data_hora}\n\n"
        "🚀 Interessado em *bônus* e *acesso VIP*."
    )

    # Log no Render
    print(f"[LEAD] {nome} | @{username} | {user_id} | {data_hora}")

    # Enviar para o admin
    try:
        bot.send_message(ADMIN_ID, texto, parse_mode="Markdown")
    except Exception as e:
        print(f"[LEAD] Erro ao enviar lead para o admin: {e}")


# ===== COMANDO /START =====

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    # 1) Enviar banner
    try:
        with open(BANNER_PATH, "rb") as banner:
            bot.send_photo(chat_id, banner)
    except Exception as e:
        print(f"[BANNER] Erro ao enviar banner: {e}")

    # 2) Teclado com opções
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎯 Quero bônus e acesso VIP", callback_data="lead_vip")
    btn2 = types.InlineKeyboardButton("ℹ️ Informações sobre a Rede Pop", callback_data="info")
    btn3 = types.InlineKeyboardButton("👨‍💼 Falar com o Agente da Rede Pop", url=LINK_CONTATO)
    btn4 = types.InlineKeyboardButton("🎰 Jogar agora na POPVAI", url=LINK_POPVAI)

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)

    # 3) Mensagem de boas-vindas
    texto = (
        "👋 Olá, tudo bem?\n\n"
        "Sou o *Bot de Informações da Rede Pop*, gerenciado por "
        "*Wericky DK (Agente da Rede Pop)*.\n\n"
        "Aqui você pode:\n"
        "• Entender como a plataforma funciona\n"
        "• Solicitar orientação profissional\n"
        "• Ter acesso a bônus e grupo VIP com suporte direto\n\n"
        "Selecione uma opção abaixo para continuar 👇"
    )

    bot.send_message(chat_id, texto, parse_mode="Markdown", reply_markup=markup)


# ===== CALLBACK DOS BOTÕES =====

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "lead_vip":
        # Registrar lead com data e horário
        registrar_lead(call.from_user)

        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🎁 Entrar no Grupo VIP", url=LINK_CONTATO)
        markup.add(btn)

        bot.send_message(
            chat_id,
            "🎯 *Acesso a Bônus e Grupo VIP com suporte direto!*\n\n"
            "👉 Clique abaixo e entre agora 👇",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif call.data == "info":
        bot.send_message(
            chat_id,
            "📊 *Informações sobre a Rede Pop:*\n\n"
            "A *Rede Pop* é uma plataforma moderna de entretenimento digital, "
            "com suporte personalizado e sistema de bônus exclusivo para novos jogadores.\n\n"
            "🎰 Na plataforma *POPVAI* você joga pelo link abaixo e fala com o "
            "Agente Wericky DK para tirar dúvidas e garantir seus bônus.",
            parse_mode="Markdown"
        )


# ===== FLASK PARA O RENDER (MANTER SERVIÇO ONLINE) =====

app = Flask(__name__)

@app.route("/")
def index():
    return "Rede Pop Info Bot está rodando!"


def iniciar_bot():
    print("🤖 Rede Pop Info Bot iniciado com sucesso!")
    bot.polling(none_stop=True, timeout=60)


if __name__ == "__main__":
    # Thread para o bot
    t = threading.Thread(target=iniciar_bot)
    t.daemon = True
    t.start()

    # Servidor web para o Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
