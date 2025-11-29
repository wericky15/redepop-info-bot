# === REDE POP INFO BOT 2.4 ===
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

    btn1 = types.InlineKeyboardButton(
        "🎯 Quero bônus e acesso VIP",
        callback_data="lead_vip"
    )
    btn2 = types.InlineKeyboardButton(
        "ℹ️ Informações sobre a Rede Pop e POPVAI",
        callback_data="info"
    )
    btn3 = types.InlineKeyboardButton(
        "🚀 Lançamento POPVAI",
        callback_data="popvai_lancamento"
    )
    # botão que abre seu PV direto
    btn4 = types.InlineKeyboardButton(
        "👨‍💼 Falar com o Agente da Rede Pop",
        url=f"tg://user?id={ADMIN_ID}"
    )
    btn5 = types.InlineKeyboardButton(
        "🎰 Jogar agora na POPVAI",
        url=LINK_POPVAI
    )

    # organiza em linhas
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5)

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

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=criar_menu_principal()
    )


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


# ===== TELAS DE INFORMAÇÃO =====

def enviar_menu_info(chat_id):
    """Mini-menu de informações (Rede Pop / PopVai / Bônus / FAQ)."""
    texto = (
        "ℹ️ *Informações sobre a Rede Pop e POPVAI*\n\n"
        "Escolha o que você quer saber:\n"
        "• O que é a Rede Pop\n"
        "• Como funciona a POPVAI\n"
        "• Bônus e Grupo VIP\n"
        "• Perguntas frequentes (FAQ)\n\n"
        "Clique em uma das opções abaixo 👇"
    )

    markup = types.InlineKeyboardMarkup()
    btn_redepop = types.InlineKeyboardButton(
        "ℹ️ O que é a Rede Pop", callback_data="info_redepop"
    )
    btn_popvai = types.InlineKeyboardButton(
        "🎰 Como funciona a POPVAI", callback_data="info_popvai"
    )
    btn_bonus = types.InlineKeyboardButton(
        "🎁 Bônus e Grupo VIP", callback_data="info_bonus"
    )
    btn_faq = types.InlineKeyboardButton(
        "❓ Perguntas frequentes (FAQ)", callback_data="faq"
    )
    btn_back = types.InlineKeyboardButton(
        "⬅️ Voltar ao menu inicial", callback_data="menu"
    )

    markup.add(btn_redepop)
    markup.add(btn_popvai)
    markup.add(btn_bonus)
    markup.add(btn_faq)
    markup.add(btn_back)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


def enviar_info_redepop(chat_id):
    texto = (
        "ℹ️ *O que é a Rede Pop?*\n\n"
        "A *Rede Pop* é um conjunto de plataformas de entretenimento online, "
        "focadas em jogos rápidos, slots e campanhas com bônus atrativos.\n\n"
        "📌 Objetivo da Rede Pop:\n"
        "• Trazer plataformas confiáveis para o jogador\n"
        "• Oferecer promoções frequentes\n"
        "• Ter suporte próximo através de agentes oficiais, como o *Wericky DK*.\n\n"
        "Sempre utilize links oficiais indicados pelo agente para garantir "
        "que você está entrando na plataforma correta. ✅"
    )

    markup = types.InlineKeyboardMarkup()
    btn_back_info = types.InlineKeyboardButton(
        "⬅️ Voltar às informações", callback_data="info"
    )
    btn_back_menu = types.InlineKeyboardButton(
        "🏠 Voltar ao menu inicial", callback_data="menu"
    )
    markup.add(btn_back_info)
    markup.add(btn_back_menu)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


def enviar_info_popvai(chat_id):
    texto = (
        "🎰 *Como funciona a POPVAI?*\n\n"
        "A *POPVAI* é uma das plataformas da Rede Pop, focada em:\n"
        "• Jogos de slots\n"
        "• Jogos rápidos\n"
        "• Campanhas de bônus e promoções especiais\n\n"
        "💳 *Depósitos e saques*: Você consegue jogar com valores acessíveis, "
        "e realizar saques dentro das regras da plataforma.\n\n"
        "🧠 *Vantagem de ter o Agente Wericky DK*:\n"
        "• Orientação para organizar banca\n"
        "• Dicas de como aproveitar melhor os bônus\n"
        "• Suporte quando tiver dúvidas.\n\n"
        "Para entrar corretamente na POPVAI use sempre o link abaixo 👇"
    )

    markup = types.InlineKeyboardMarkup()
    btn_play = types.InlineKeyboardButton(
        "🎰 Jogar agora na POPVAI", url=LINK_POPVAI
    )
    btn_back_info = types.InlineKeyboardButton(
        "⬅️ Voltar às informações", callback_data="info"
    )
    btn_back_menu = types.InlineKeyboardButton(
        "🏠 Voltar ao menu inicial", callback_data="menu"
    )

    markup.add(btn_play)
    markup.add(btn_back_info)
    markup.add(btn_back_menu)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


def enviar_info_bonus(chat_id):
    texto = (
        "🎁 *Bônus e Grupo VIP da Rede Pop*\n\n"
        "No *Grupo VIP* com o Agente *Wericky DK* você pode:\n"
        "• Saber quais bônus estão ativos no momento\n"
        "• Receber estratégias de banca\n"
        "• Tirar dúvidas antes de depositar\n\n"
        "📌 *Como funciona em geral:*\n"
        "1️⃣ Você entra em uma plataforma oficial da Rede Pop (como a POPVAI);\n"
        "2️⃣ Fala com o agente para entender a melhor forma de depositar;\n"
        "3️⃣ Recebe orientações sobre bônus, metas e controle de banca.\n\n"
        "Entre no Grupo VIP para ser atendido diretamente 👇"
    )

    markup = types.InlineKeyboardMarkup()
    btn_vip = types.InlineKeyboardButton(
        "🎁 Entrar no Grupo VIP", url=GROUP_VIP_LINK
    )
    btn_back_info = types.InlineKeyboardButton(
        "⬅️ Voltar às informações", callback_data="info"
    )
    btn_back_menu = types.InlineKeyboardButton(
        "🏠 Voltar ao menu inicial", callback_data="menu"
    )

    markup.add(btn_vip)
    markup.add(btn_back_info)
    markup.add(btn_back_menu)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


def enviar_faq(chat_id):
    texto = (
        "❓ *Perguntas frequentes (FAQ)*\n\n"
        "🔹 *1. Qual o depósito mínimo?*\n"
        "Cada campanha pode ter um valor mínimo diferente. No geral, os depósitos "
        "são acessíveis, mas o ideal é falar com o *Agente Wericky DK* para saber "
        "qual é o melhor valor para o seu objetivo.\n\n"
        "🔹 *2. Consigo sacar mesmo jogando com bônus?*\n"
        "Sim, desde que siga as regras da plataforma e das promoções. "
        "Sempre confira as condições e, em caso de dúvida, fale com o agente.\n\n"
        "🔹 *3. Onde eu falo com o suporte?*\n"
        "Você pode contar com o suporte do *Agente Wericky DK* no Grupo VIP ou no PV.\n\n"
        "🔹 *4. Bônus é garantia de ganhar?*\n"
        "Não. Bônus ajuda a aumentar o tempo de jogo e as chances de rodadas, "
        "mas não garante lucro. Jogue sempre com responsabilidade.\n\n"
        "Se ainda ficou alguma dúvida, fale com o agente ou entre no Grupo VIP 👇"
    )

    markup = types.InlineKeyboardMarkup()
    btn_vip = types.InlineKeyboardButton(
        "🎁 Entrar no Grupo VIP", url=GROUP_VIP_LINK
    )
    btn_agent = types.InlineKeyboardButton(
        "👨‍💼 Falar com o Agente", url=f"tg://user?id={ADMIN_ID}"
    )
    btn_back_info = types.InlineKeyboardButton(
        "⬅️ Voltar às informações", callback_data="info"
    )
    btn_back_menu = types.InlineKeyboardButton(
        "🏠 Voltar ao menu inicial", callback_data="menu"
    )

    markup.add(btn_vip)
    markup.add(btn_agent)
    markup.add(btn_back_info)
    markup.add(btn_back_menu)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


# ===== TELA ESPECIAL — LANÇAMENTO POPVAI =====

def enviar_popvai_lancamento(chat_id):
    texto = (
        "🚀 *LANÇAMENTO OFICIAL POPVAI* 🚀\n\n"
        "A *POPVAI* é a nova plataforma da *Rede Pop*, pensada para quem quer:\n"
        "• Jogos de slots com muita dinâmica\n"
        "• Jogos rápidos para giro de banca\n"
        "• Campanhas especiais de lançamento\n\n"
        "🎯 *Por que entrar agora no lançamento?*\n"
        "• Campanhas promocionais ativas por tempo limitado\n"
        "• Acompanhamento direto com o *Agente Wericky DK*\n"
        "• Orientação para não se perder na banca e jogar com mais consciência\n\n"
        "⚠️ Lembre-se: não existe garantia de lucro. Jogue sempre com "
        "responsabilidade e apenas com o que não vai te fazer falta.\n\n"
        "Clique abaixo para entrar pela *POPVAI oficial* e depois fale com o agente 👇"
    )

    markup = types.InlineKeyboardMarkup()
    btn_play = types.InlineKeyboardButton(
        "🎰 Jogar agora na POPVAI", url=LINK_POPVAI
    )
    btn_agent = types.InlineKeyboardButton(
        "👨‍💼 Falar com o Agente", url=f"tg://user?id={ADMIN_ID}"
    )
    btn_vip = types.InlineKeyboardButton(
        "🎁 Entrar no Grupo VIP", url=GROUP_VIP_LINK
    )
    btn_back_menu = types.InlineKeyboardButton(
        "🏠 Voltar ao menu inicial", callback_data="menu"
    )

    markup.add(btn_play)
    markup.add(btn_agent)
    markup.add(btn_vip)
    markup.add(btn_back_menu)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


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
            # Abre o mini-menu de informações
            enviar_menu_info(chat_id)

        elif call.data == "info_redepop":
            enviar_info_redepop(chat_id)

        elif call.data == "info_popvai":
            enviar_info_popvai(chat_id)

        elif call.data == "info_bonus":
            enviar_info_bonus(chat_id)

        elif call.data == "faq":
            enviar_faq(chat_id)

        elif call.data == "popvai_lancamento":
            enviar_popvai_lancamento(chat_id)

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
