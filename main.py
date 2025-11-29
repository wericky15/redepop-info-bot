# === REDE POP INFO BOT 3.0 (CONVERSÃO) ===
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

# Link base da plataforma POPVAI (sem UTM extra)
BASE_LINK_POPVAI = "https://11popvai.com/?pid=3291819190"

# Link do grupo VIP (o seu grupo no Telegram)
GROUP_VIP_LINK = "https://t.me/werickyredpop"

bot = telebot.TeleBot(BOT_TOKEN)

# ===== CONTADORES EM MEMÓRIA =====
TOTAL_STARTS = 0
TOTAL_LEADS = 0
USUARIOS_LEAD = set()

TOTAL_INFO_MENU = 0
TOTAL_INFO_POPVAI = 0
TOTAL_INFO_BONUS = 0
TOTAL_INFO_FAQ = 0
TOTAL_LANCAMENTO_POPVAI = 0

# "Vagas VIP" para gatilho de urgência (FOMO)
VAGAS_VIP_INICIAIS = 20
VAGAS_VIP_MINIMO = 3
VAGAS_VIP_ATUAIS = VAGAS_VIP_INICIAIS


# ===== FUNÇÃO PARA GERAR LINK POPVAI COM UTM =====

def gerar_link_popvai(user_id=None, origem="default"):
    """
    Gera o link da POPVAI com parâmetros UTM e ID do usuário.
    Se não tiver user_id, usa só o link base.
    """
    if user_id:
        return (
            f"{BASE_LINK_POPVAI}"
            f"&utm_source=bot_redepop"
            f"&utm_medium=telegram"
            f"&utm_campaign={origem}"
            f"&utm_userid={user_id}"
        )
    else:
        return BASE_LINK_POPVAI


# ===== FUNÇÃO PARA CRIAR MENU PRINCIPAL =====

def criar_menu_principal(user_id=None):
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
        url=gerar_link_popvai(user_id, origem="menu_principal")
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
    global TOTAL_LEADS, USUARIOS_LEAD, VAGAS_VIP_ATUAIS

    nome = user.first_name or "Sem nome"
    username = user.username or "sem_username"
    user_id = user.id
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Contadores
    TOTAL_LEADS += 1
    USUARIOS_LEAD.add(user_id)

    # Diminuir vagas VIP mas nunca abaixo do mínimo
    if VAGAS_VIP_ATUAIS > VAGAS_VIP_MINIMO:
        VAGAS_VIP_ATUAIS -= 1

    texto_admin = (
        "📥 *NOVO LEAD REDE POP*\n\n"
        f"👤 *Nome:* {nome}\n"
        f"📛 *Username:* @{username}\n"
        f"🆔 *ID:* `{user_id}`\n"
        f"⏰ *Data e horário:* {data_hora}\n\n"
        "🚀 Interessado em *bônus* e *acesso VIP*.\n"
        f"🎯 Total de leads: *{TOTAL_LEADS}*\n"
        f"🔥 Vagas VIP (gatilho): *{VAGAS_VIP_ATUAIS}* restantes."
    )

    print(f"[LEAD] {nome} | @{username} | {user_id} | {data_hora}")

    try:
        bot.send_message(ADMIN_ID, texto_admin, parse_mode="Markdown")
    except Exception as e:
        print(f"[LEAD] Erro ao enviar lead para o admin: {e}")


# ===== MENSAGEM DE BOAS-VINDAS + MENU =====

def enviar_menu_inicial(chat_id, user_id=None):
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
        reply_markup=criar_menu_principal(user_id)
    )


# ===== COMANDO /START =====

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global TOTAL_STARTS

    chat_id = message.chat.id
    user_id = message.from_user.id
    TOTAL_STARTS += 1  # Contador de /start

    # 1) Enviar banner
    try:
        with open(BANNER_PATH, "rb") as banner:
            bot.send_photo(chat_id, banner)
    except Exception as e:
        print(f"[BANNER] Erro ao enviar banner: {e}")

    # 2) Mensagem + menu
    enviar_menu_inicial(chat_id, user_id)


# ===== COMANDO /STATS (APENAS ADMIN) =====

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return  # Ignora se não for o admin

    texto = (
        "📊 *ESTATÍSTICAS DO BOT REDE POP INFO*\n\n"
        f"▶️ *Inícios (/start):* {TOTAL_STARTS}\n\n"
        f"🎯 *Cliques em \"Quero bônus e acesso VIP\":*\n"
        f"   • Total de cliques: {TOTAL_LEADS}\n"
        f"   • Leads únicos: {len(USUARIOS_LEAD)}\n"
        f"   • Vagas VIP (gatilho FOMO): {VAGAS_VIP_ATUAIS}\n\n"
        f"ℹ️ *Informações acessadas:*\n"
        f"   • Menu de informações aberto: {TOTAL_INFO_MENU}\n"
        f"   • Tela \"Como funciona a POPVAI\": {TOTAL_INFO_POPVAI}\n"
        f"   • Tela \"Bônus e Grupo VIP\": {TOTAL_INFO_BONUS}\n"
        f"   • FAQ aberta: {TOTAL_INFO_FAQ}\n\n"
        f"🚀 *Lançamento POPVAI aberto:* {TOTAL_LANCAMENTO_POPVAI} vezes\n\n"
        "_Obs: esses contadores são em memória e zeram se o bot for reiniciado._"
    )

    bot.send_message(
        message.chat.id,
        texto,
        parse_mode="Markdown"
    )


# ===== TELAS DE INFORMAÇÃO =====

def enviar_menu_info(chat_id):
    """Mini-menu de informações (Rede Pop / PopVai / Bônus / FAQ)."""
    global TOTAL_INFO_MENU
    TOTAL_INFO_MENU += 1

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


def enviar_info_popvai(chat_id, user_id=None):
    global TOTAL_INFO_POPVAI
    TOTAL_INFO_POPVAI += 1

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
        "🎰 Jogar agora na POPVAI",
        url=gerar_link_popvai(user_id, origem="info_popvai")
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


def enviar_info_bonus(chat_id, user_id=None):
    global TOTAL_INFO_BONUS
    TOTAL_INFO_BONUS += 1

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
    btn_play = types.InlineKeyboardButton(
        "🎰 Jogar na POPVAI",
        url=gerar_link_popvai(user_id, origem="info_bonus")
    )
    btn_back_info = types.InlineKeyboardButton(
        "⬅️ Voltar às informações", callback_data="info"
    )
    btn_back_menu = types.InlineKeyboardButton(
        "🏠 Voltar ao menu inicial", callback_data="menu"
    )

    markup.add(btn_vip)
    markup.add(btn_play)
    markup.add(btn_back_info)
    markup.add(btn_back_menu)

    bot.send_message(
        chat_id,
        texto,
        parse_mode="Markdown",
        reply_markup=markup
    )


def enviar_faq(chat_id):
    global TOTAL_INFO_FAQ
    TOTAL_INFO_FAQ += 1

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


# ===== TELA — LANÇAMENTO POPVAI =====

def enviar_popvai_lancamento(chat_id, user_id=None):
    global TOTAL_LANCAMENTO_POPVAI
    TOTAL_LANCAMENTO_POPVAI += 1

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
        "🔥 *Prova social:*\n"
        f"• Jogadores que já solicitaram bônus pelo bot: *{TOTAL_LEADS}*\n"
        f"• Vagas VIP disponíveis hoje: *{VAGAS_VIP_ATUAIS}*\n\n"
        "⚠️ Não existe garantia de lucro. Jogue sempre com responsabilidade "
        "e apenas com o que não vai te fazer falta.\n\n"
        "Clique abaixo para entrar pela *POPVAI oficial* e depois fale com o agente 👇"
    )

    markup = types.InlineKeyboardMarkup()
    btn_play = types.InlineKeyboardButton(
        "🎰 Jogar agora na POPVAI",
        url=gerar_link_popvai(user_id, origem="lancamento_popvai")
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
    user = call.from_user
    user_id = user.id

    try:
        if call.data == "lead_vip":
            # Registrar lead com data e horário + contador + vagas
            registrar_lead(user)

            # Mensagem no chat (com prova social e FOMO)
            markup = types.InlineKeyboardMarkup()
            btn_vip = types.InlineKeyboardButton(
                "🎁 Entrar no Grupo VIP", url=GROUP_VIP_LINK
            )
            btn_play = types.InlineKeyboardButton(
                "🎰 Jogar agora na POPVAI",
                url=gerar_link_popvai(user_id, origem="lead_vip")
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
                f"🔥 *Vagas VIP disponíveis hoje:* {VAGAS_VIP_ATUAIS}\n"
                f"👥 *Pessoas que já solicitaram bônus pelo bot:* {TOTAL_LEADS}\n\n"
                "👉 Entre no grupo VIP para falar com o Agente Wericky DK, tirar dúvidas "
                "e receber orientações de bônus.\n\n"
                "Vo
