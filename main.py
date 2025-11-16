import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# 🔑 Token vem das variáveis de ambiente do Render
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN não encontrado. Defina a variável de ambiente no Render.")

bot = telebot.TeleBot(TOKEN)

# 🔗 SEUS LINKS / CONTATO
LINK_PLATAFORMA = "https://33popn1.com/?pid=3779132759"   # seu link da Pop
LINK_RTP = ""                                            # se quiser depois, coloque aqui o link do seu site RTP
USER_SUPORTE = "@WerickyDK"                              # seu @ no Telegram

# ------------ MENUS ------------ #

def criar_menu_principal():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📌 O que é a Rede Pop?", callback_data="info_oquee")
    )
    markup.row(
        InlineKeyboardButton("💰 Como depositar", callback_data="info_deposito"),
        InlineKeyboardButton("💸 Como sacar", callback_data="info_saque")
    )
    markup.row(
        InlineKeyboardButton("🎁 Bônus e promoções", callback_data="info_bonus")
    )
    markup.row(
        InlineKeyboardButton("📊 RTP / Dicas de jogos", callback_data="info_rtp")
    )
    markup.row(
        InlineKeyboardButton("🎯 Entrar na plataforma", url=LINK_PLATAFORMA)
    )
    markup.row(
        InlineKeyboardButton(
            "🧑‍💻 Falar com o gerente",
            url=f"https://t.me/{USER_SUPORTE.replace('@','')}"
        )
    )
    return markup


def criar_botoes_chamada(incluir_rtp=False):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎯 Entrar na plataforma", url=LINK_PLATAFORMA)
    )
    if incluir_rtp and LINK_RTP:
        markup.row(
            InlineKeyboardButton("📊 Ver RTP agora", url=LINK_RTP)
        )
    markup.row(
        InlineKeyboardButton(
            "🧑‍💻 Falar com o gerente",
            url=f"https://t.me/{USER_SUPORTE.replace('@','')}"
        )
    )
    markup.row(
        InlineKeyboardButton("⬅ Voltar ao menu", callback_data="voltar_menu")
    )
    return markup

# ------------ HANDLERS DO BOT ------------ #

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    texto = (
        "👋 Seja bem-vindo ao *Bot de Informações Rede Pop*.\n\n"
        "Aqui você tira dúvidas sobre a plataforma e ainda pode entrar "
        "pelo meu link com suporte completo.\n\n"
        "Escolha uma opção no menu abaixo 👇"
    )
    bot.send_message(
        message.chat.id,
        texto,
        reply_markup=criar_menu_principal(),
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data

    if data == "info_oquee":
        texto = (
            "📌 *O que é a Rede Pop?*\n\n"
            "Plataforma de jogos/slots com vários provedores, bônus e promoções.\n"
            "Você joga com responsabilidade e aproveita campanhas, missões e ofertas.\n"
        )
        botoes = criar_botoes_chamada()

    elif data == "info_deposito":
        texto = (
            "💰 *Como depositar na Rede Pop*\n\n"
            "1️⃣ Clique em *Entrar na plataforma* abaixo.\n"
            "2️⃣ Faça seu cadastro ou login.\n"
            "3️⃣ Vá em *Depósito*.\n"
            "4️⃣ Escolha PIX (ou outro método) e siga as instruções.\n\n"
            "Se travar em alguma parte, me chama no privado. 😉"
        )
        botoes = criar_botoes_chamada()

    elif data == "info_saque":
        texto = (
            "💸 *Como sacar na Rede Pop*\n\n"
            "1️⃣ Confira se cumpriu as regras de bônus/rollover.\n"
            "2️⃣ Vá em *Saque* na plataforma.\n"
            "3️⃣ Escolha PIX e informe os dados certinho.\n"
            "4️⃣ Confirme e aguarde o processamento.\n\n"
            "Dúvida sobre limite, tempo ou erro? Fala comigo. 👇"
        )
        botoes = criar_botoes_chamada()

    elif data == "info_bonus":
        texto = (
            "🎁 *Bônus e promoções*\n\n"
            "A Rede Pop costuma ter bônus de cadastro, recarga e campanhas especiais.\n\n"
            "Eu aviso sempre as melhores oportunidades pra quem entra pelo meu link.\n"
            "Entre na plataforma pelo botão abaixo e fala comigo pra eu te orientar no bônus do dia. 🔥"
        )
        botoes = criar_botoes_chamada()

    elif data == "info_rtp":
        texto = (
            "📊 *RTP / Dicas de jogos*\n\n"
            "RTP é a taxa de retorno teórico do jogo.\n"
            "Eu acompanho os jogos que estão rodando melhor no momento.\n"
        )
        if LINK_RTP:
            texto += "🔗 Veja uma lista de jogos/RTP clicando no botão abaixo.\n"
            botoes = criar_botoes_chamada(incluir_rtp=True)
        else:
            texto += "Quer dicas atualizadas? Me chama no privado. 😉\n"
            botoes = criar_botoes_chamada()

    elif data == "voltar_menu":
        bot.edit_message_text(
            "Escolha uma opção no menu abaixo 👇",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=criar_menu_principal()
        )
        return
    else:
        return

    bot.edit_message_text(
        texto,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=botoes,
        parse_mode="Markdown"
    )

# ------------ FLASK + THREAD DO BOT ------------ #

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Rede Pop Info - OK"

def iniciar_bot():
    print("Iniciando bot Telegram (polling)...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # inicia o bot em uma thread separada
    t = threading.Thread(target=iniciar_bot, daemon=True)
    t.start()

    # inicia o servidor web para o Render
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor Flask rodando na porta {port}...")
    app.run(host="0.0.0.0", port=port)

