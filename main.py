import discord
from discord.ext import commands
import smtplib
from twilio.rest import Client

# Configuración
DISCORD_TOKEN = "TU_TOKEN_DEL_BOT"
CHANNEL_ID = 1234567890123456  # Reemplaza con el ID del canal a monitorear

# Config Email (Gmail)
EMAIL_FROM = "tu_email@gmail.com"
EMAIL_PASS = "contraseña_app"  # Usa "Contraseña de aplicación"
EMAIL_TO = "email_destino@example.com"

# Config WhatsApp (Twilio)
TWILIO_SID = "tu_account_sid"
TWILIO_TOKEN = "tu_auth_token"
TWILIO_PHONE = "whatsapp:+14155238886"  # Número de Twilio
YOUR_PHONE = "whatsapp:+521234567890"   # Tu número con código país

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID and not message.author.bot:
        content = f"Nuevo mensaje en {message.guild.name} - #{message.channel.name}:\n{message.author}: {message.content}"
        
        # Enviar por Email
        send_email(content)
        
        # Enviar por WhatsApp
        send_whatsapp(content)
        
    await bot.process_commands(message)

def send_email(content):
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            subject = "🚨 Nuevo mensaje en Discord!"
            msg = f"Subject: {subject}\n\n{content}"
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.encode('utf-8'))
    except Exception as e:
        print("Error al enviar email:", e)

def send_whatsapp(content):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=content,
            from_=TWILIO_PHONE,
            to=YOUR_PHONE
        )
    except Exception as e:
        print("Error al enviar WhatsApp:", e)

bot.run(DISCORD_TOKEN)