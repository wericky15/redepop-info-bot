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
LINK_RTP = ""                                             # se quiser depois, coloque aqui o link do seu site RTP
USER_SUPORTE = "@Whsantosz"                               # seu @ no Telegram
LINK_GRUPO_VIP = "https://t.me/werickyredpop"             # seu grupo VIP

# ------------ MENUS / TECLADOS ------------ #

def criar_menu_inicial():
    """
    Menu focado em conversão:
    - Lead para bônus / VIP
    - Informações da plataforma
    - Contato com Agente Oficial
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎯 Quero bônus e acesso VIP", callback_data="lead_vip")
    )
    markup.row(
        InlineKeyboardButton("ℹ Informações sobre a Rede Pop", callback_data="menu_info")
    )
    markup.row(
        InlineKeyboardButton(
            "👨‍💼 Falar com o Agente Oficial",
            url=f"https://t.me/{USER_SUPORTE.replace('@','')}"
        )
    )
    return markup


def criar_menu_info():
    """
    Menu de informações gerais sobre a Rede Pop.
    """
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
        InlineKeyboardButton("⬅ Voltar", callback_data="voltar_inicio")
    )
    return markup


def criar_botoes_conversao(incluir_rtp=False):
    """
    Botões para conversão direta: plataforma, grupo VIP, contato.
    """
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
            url=f"https://t.me/{USER_SUPORTE.replace('@','')}"
        )
    )
    if incluir_rtp and LINK_RTP:
        markup.row(
            InlineKeyboardButton("📊 Ver RTP dos Jogos", url=https://redepop-rtp.netlify.app/)
        )
    markup.row(
        InlineKeyboardButton("⬅ Voltar ao início", callback_data="voltar_inicio")
    )
    return markup


# ------------ REGISTRO DE LEADS ------------ #

def registrar_lead(user):
    """
    Registra nos logs um jogador que demonstrou interesse em bônus / VIP.
    Você consegue ver isso na aba Logs do Render.
    """
    username = user.username or ""
    first_name = user.first_name or ""
    user_id = user.id
    print(f"[LEAD] Novo jogador interessado: {first_name} (@{username}) id={user_id}")


# ------------ HANDLERS DO BOT ------------ #

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    texto = (
        "👋 Olá, tudo bem?\n\n"
        "Sou o *Bot Oficial de Informações da Rede Pop*, gerenciado pelo "
        "*Wericky DK (Agente Oficial)*.\n\n"
        "Aqui você pode:\n"
        "• Entender como a plataforma funciona\n"
        "• Solicitar orientação profissional\n"
        "• Ter acesso a bônus e grupo VIP com suporte direto\n\n"
        "Selecione uma opção abaixo para continuar 👇"
    )
    bot.send_message(
        message.chat.id,
        texto,
        reply_markup=criar_menu_inicial(),
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data

    # Lead de bônus / VIP
    if data == "lead_vip":
        registrar_lead(call.from_user)
        texto = (
            "🎯 *Acesso a Bônus e Grupo VIP*\n\n"
            "Você demonstrou interesse em receber orientação profissional, "
            "acesso a bônus e participar do grupo VIP.\n\n"
            "Abaixo estão as opções para você avançar de forma segura:"
        )
        botoes = criar_botoes_conversao(incluir_rtp=bool(LINK_RTP))

        bot.edit_message_text(
            texto,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=botoes,
            parse_mode="Markdown"
        )
        return

    # Menu de informações
    if data == "menu_info":
        bot.edit_message_text(
            "ℹ *Informações sobre a Rede Pop*\n\n"
            "Escolha uma das opções abaixo:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=criar_menu_info(),
            parse_mode="Markdown"
        )
        return

    # Voltar ao início
    if data == "voltar_inicio":
        bot.edit_message_text(
            "Selecione uma opção para continuar 👇",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=criar_menu_inicial()
        )
        return

    # Informações detalhadas
    if data == "info_oquee":
        texto = (
            "📌 *O que é a Rede Pop?*\n\n"
            "A Rede Pop é uma plataforma de jogos/slots com diversos provedores, "
            "campanhas de bônus e oportunidades diárias.\n\n"
            "Trabalhando com responsabilidade, é possível aproveitar melhor "
            "os benefícios oferecidos pela plataforma."
        )
        botoes = criar_botoes_conversao(incluir_rtp=False)

    elif data == "info_deposito":
        texto = (
            "💰 *Como depositar na Rede Pop*\n\n"
            "1️⃣ Acesse a plataforma pelo botão *Entrar na Plataforma*.\n"
            "2️⃣ Realize seu cadastro ou login.\n"
            "3️⃣ No menu interno, selecione *Depósito*.\n"
            "4️⃣ Escolha o método disponível (PIX, por exemplo) e siga as instruções.\n\n"
            "Em caso de dúvidas, utilize o botão para falar diretamente com o Gerente Geral."
        )
        botoes = criar_botoes_conversao(incluir_rtp=False)

    elif data == "info_saque":
        texto = (
            "💸 *Como sacar na Rede Pop*\n\n"
            "1️⃣ Verifique se cumpriu todas as condições de bônus/rollover, caso tenha utilizado.\n"
            "2️⃣ No menu da plataforma, selecione *Saque*.\n"
            "3️⃣ Escolha o método desejado (como PIX) e informe os dados corretamente.\n"
            "4️⃣ Confirme a operação e aguarde o processamento.\n\n"
            "Se houver qualquer divergência, o suporte via Gerente Geral está à disposição."
        )
        botoes = criar_botoes_conversao(incluir_rtp=False)

    elif data == "info_bonus":
        texto = (
            "🎁 *Bônus e promoções*\n\n"
            "A plataforma trabalha com campanhas de bônus que podem incluir:\n"
            "• Bônus de cadastro\n"
            "• Bônus de recarga\n"
            "• Campanhas sazonais\n\n"
            "As melhores oportunidades e orientações são fornecidas diretamente "
            "para quem entra pelo meu link e participa do grupo VIP."
        )
        botoes = criar_botoes_conversao(incluir_rtp=False)

    elif data == "info_rtp":
        texto = (
            "📊 *RTP / Dicas de jogos*\n\n"
            "O RTP (Retorno Teórico ao Jogador) indica, em teoria, quanto um jogo "
            "tende a devolver no longo prazo.\n\n"
            "Eu acompanho constantemente os jogos que estão com melhor desempenho "
            "e oriento de forma profissional."
        )
        if LINK_RTP:
            texto += "\n\nVocê pode acessar uma lista de jogos e RTP pelo botão abaixo."
            botoes = criar_botoes_conversao(incluir_rtp=True)
        else:
            texto += "\n\nPara receber indicações atualizadas, utilize o botão para falar diretamente comigo."
            botoes = criar_botoes_conversao(incluir_rtp=False)
    else:
        return  # callback desconhecido, não faz nada

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
