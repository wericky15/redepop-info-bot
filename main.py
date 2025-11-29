import telebot
from telebot import types
import os
from datetime import datetime

# === CONFIGURAÇÃO DO BOT ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# === SEU ID (Wericky DK) ===
ADMIN_ID = 8586126783  # Seu ID do Telegram para receber os leads

bot = telebot.TeleBot(BOT_TOKEN)


# === FUNÇÃO DE REGISTRO DE LEAD ===
def registrar_lead(user):
    nome = user.first_name or ""
    username = user.username or ""
    user_id = user.id
    data = datetime.now().strftime("%d/%m/%Y %H:%M")

    texto = (
        "📥 *NOVO LEAD REDE POP*\n\n"
        f"👤 *Nome:* {nome}\n"
        f"📛 *Username:* @{username if username else 'sem username'}\n"
        f"🆔 *ID:* {user_id}\n"
        f"⏰ *Data:* {data}"
    )

    # Log no Render
    print(f"[LEAD] {nome} | @{username} | {user_id} | {data}")

    # Enviar mensagem para você (admin)
    try:
        bot.send_message(ADMIN_ID, texto, parse_mode="Markdown")
    except Exception as e:
        print(f"[LEAD] Erro ao enviar lead para o admin: {e}")


# === COMANDO /START ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎯 Quero bônus e acesso VIP", callback_data="lead_vip")
    btn2 = types.InlineKeyboardButton("ℹ️ Informações sobre a Rede Pop", callback_data="info")
    btn3 = types.InlineKeyboardButton("👨‍💼 Falar com o Agente Oficial", url="https://t.me/werickyredpop")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)

    texto = (
        "👋 Olá, tudo bem?\n\n"
        "Sou o *Bot Oficial de Informações da Rede Pop*, gerenciado por "
        "*Wericky DK (Agente Oficial da Rede Pop)*.\n\n"
        "Aqui você pode:\n"
        "• Entender como a plataforma funciona\n"
        "• Solicitar orientação profissional\n"
        "• Ter acesso a bônus e grupo VIP com suporte direto\n\n"
        "Selecione uma opção abaixo para continuar 👇"
    )
    bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)


# === CALLBACKS DOS BOTÕES ===
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "lead_vip":
        registrar_lead(call.from_user)
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🎁 Entrar no Grupo VIP", url="https://t.me/werickyredpop")
        markup.add(btn)
        bot.send_message(
            call.message.chat.id,
            "🎯 Acesso a Bônus e Grupo VIP com suporte direto.\n\n"
            "👉 Clique abaixo e entre agora:",
            reply_markup=markup
        )

    elif call.data == "info":
        bot.send_message(
            call.message.chat.id,
            "📊 *Informações sobre a Rede Pop:*\n\n"
            "A Rede Pop é uma plataforma moderna de entretenimento digital, "
            "com suporte personalizado e sistema de bônus exclusivo.\n\n"
            "🎁 Quer começar agora e garantir o bônus de boas-vindas?\n"
            "Use o botão abaixo para acessar:",
            parse_mode="Markdown"
        )


# === LOOP PRINCIPAL ===
bot.polling(none_stop=True)

