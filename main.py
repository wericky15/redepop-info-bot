# === REDE POP INFO BOT 2.2 ===
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

if not BOT_TOKEN:
    print("ERRO: BOT_TOKEN não definido nas variáveis de ambiente!")

# Seu ID para receber os leads e abrir o PV no botão de contato
ADMIN_ID = 8586126783  # Wericky DK

# Nome do arquivo do banner que você renomeou no GitHub
BANNER_PATH = "banner.png"

# Link da plataforma POPVAI
LINK_POPVAI = "https://11popvai.com/?pid=3291819190"

# Link do grupo VIP (o seu grupo no Telegram)
GROUP_VIP_LINK = "https://t.me/werickyredpop"

bot = telebot.TeleBot(BOT_TOKEN)


# ===== FUNÇÃO PARA CRIAR MENU PRINCIPAL =====

def criar_menu_principal():
    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("🎯 Quero bônus e acesso VIP",
                                      callback_data="lead_vip")
    btn2 = types.InlineKeyboardButton("ℹ️ Informações sobre a Rede Pop e POPVAI",
                                      callback_data="info")
    # botão que abre seu PV direto
    btn3 = types.InlineKeyboardButton(
        "👨‍💼 Falar com o Agente da Rede Pop",
        url=f"tg://user?id={ADMIN_ID}"
    )
    btn4 = types.InlineKeyboardButton("🎰 Jogar agora na POPVAI",
                                      url=LINK_POPVAI)

    # organiza em linhas
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)

    return markup


# ===== FUNÇÃO PARA REGISTRAR LEAD =====

def registrar_lead(user):
    nome = user.first_name or "Sem nome"
    username = user.username or "sem_username"
    user_id = user.id
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    texto = (
        "📥 *NOVO LEAD REDE POP*\n\n"
        f"👤 *Nome:* {nome}\n"
        f"📛 *Username:* @{username}\n"
        f"🆔 *ID:* `{user_id}`\n"
        f"⏰ *Data e horário:* {data_hora}\n\n"
        "🚀 Interessado em *bônus* e *acesso VIP*."
    )

    print(f"[LEAD] {nome} | @{username} | {user_id} | {data_hora}")

    try:
        bot.send_message(ADMIN_ID, texto, parse_mode="Markdown")
    except Exception as e:
        print(f"[LEAD] Erro ao enviar lead para o admin: {e}")


# ===== MENSAGEM DE BOAS-VINDAS + MENU =====

def enviar_menu_inicial(chat_id):
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

    bot.send_message(chat_id, texto,
                     parse_mode="Markdown",
                     reply_markup=criar_menu_principal())


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

    # 2) Mensagem + menu
    enviar_menu_inicial(chat_id)


# ===== CALLBACK DOS BOTÕES =====

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    try:
        if call.data == "lead_vip":
            # Registrar lead com data e horário
            registrar_lead(call.from_user)

            markup = types.InlineKeyboardMarkup()
            btn_vip = types.InlineKeyboardButton(
                "🎁 Entrar no Grupo VIP", url=GROUP_VIP_LINK
            )
            btn_play = types.InlineKeyboardButton(
                "🎰 Jogar agora na POPVAI", url=LINK_POPVAI
            )
            btn_back = types.InlineKeyboardButton(
                "⬅️ Voltar ao menu inicial", callback_data="menu"
            )

            markup.add(btn_vip)
            markup.add(btn_play)
            markup.add(btn_back)

            bot.send_message(
                chat_id,
                "🎯 *Acesso a Bônus e Grupo VIP com suporte direto!*\n\n"
                "👉 Entre no grupo VIP para falar com o Agente Wericky DK, tirar dúvidas "
                "e receber orientações de bônus.\n\n"
                "Você também pode clicar para *jogar agora na POPVAI* 👇",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif call.data == "info":
            markup = types.InlineKeyboardMarkup()
            btn_play = types.InlineKeyboardButton(
                "🎰 Jogar agora na POPVAI", url=LINK_POPVAI
            )
            btn_back = types.InlineKeyboardButton(
                "⬅️ Voltar ao menu inicial", callback_data="menu"
            )
            markup.add(btn_play)
            markup.add(btn_back)

            bot.send_message(
                chat_id,
                "ℹ️ *Sobre a Rede Pop e a POPVAI*\n\n"
                "A *Rede Pop* é uma rede de plataformas de entretenimento online, focada em "
                "jogos rápidos, bônus atrativos e suporte próximo ao jogador.\n\n"
                "A plataforma *POPVAI* é uma das casas da Rede Pop, onde você pode:\n"
                "• Jogar com depósitos a partir de pequenos valores\n"
                "• Participar de promoções e campanhas especiais\n"
                "• Contar com a orientação do *Agente Wericky DK* para organizar banca, "
                "entender bônus e tirar dúvidas.\n\n"
                "🎰 Para jogar pela POPVAI e já entrar com o link correto, use o botão abaixo 👇",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif call.data == "menu":
            # Voltar ao menu inicial
            enviar_menu_inicial(chat_id)

        else:
            # Qualquer callback desconhecido -> manda menu
            enviar_menu_inicial(chat_id)

    except Exception as e:
        print(f"[CALLBACK ERRO] {e}")
        enviar_menu_inicial(chat_id)


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
