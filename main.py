import telebot
from telebot import types
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Função para registrar leads no log
def registrar_lead(user):
    username = user.username or ""
    first_name = user.first_name or ""
    user_id = user.id
    print(f"[LEAD] Novo jogador interessado: {first_name} (@{username}) id={user_id}")

# Comando /start
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
        "Sou o *Bot Oficial de Informações da Rede Pop*, gerenciado por *Wericky DK (Agente Oficial da Rede Pop)*.\n\n"
        "Aqui você pode:\n"
        "• Entender como a plataforma funciona\n"
        "• Solicitar orientação profissional\n"
        "• Ter acesso a bônus e grupo VIP com suporte direto\n\n"
        "Selecione uma opção abaixo para continuar 👇"
    )

    bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)

# Respostas aos botões
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

# Mantém o bot ativo
bot.polling(none_stop=True)
