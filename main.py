import os
import discord
from discord.ext import commands
import smtplib
from twilio.rest import Client
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

load_dotenv()  

# Configuración
# Acceder a las variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Convertir a entero
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')
YOUR_PHONE = os.getenv('YOUR_PHONE')

intents = discord.Intents.default()
intents.message_content = True  # Intent para leer contenido de mensajes
intents.members = True         # Si necesitas información de miembros
intents.presences = True       # Si necesitas estados de usuarios


bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    # Añade esto para evitar conflictos con comandos
    allowed_mentions=discord.AllowedMentions.none()
)


# Variable global para almacenar el último tiempo de notificación
last_notification_time = None
COOLDOWN_MINUTES = 10  # Tiempo de espera entre notificaciones

def can_send_notification():
    global last_notification_time
    
    # Si nunca se ha enviado una notificación, permitir enviar
    if last_notification_time is None:
        return True
    
    # Calcular el tiempo actual y el tiempo del siguiente permitido
    current_time = datetime.now()
    next_allowed_time = last_notification_time + timedelta(minutes=COOLDOWN_MINUTES)
    
    # Verificar si ha pasado el tiempo de cooldown
    return current_time >= next_allowed_time


@bot.event
async def on_ready():
    print(f'Conectado como {bot.user} en {len(bot.guilds)} servidores!')
    # Prueba de que los intents funcionan
    channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
    await channel.send("¡Bot activado correctamente! ✅")

@bot.event
async def on_message(message):
    global last_notification_time
    
    # Solo procesar mensajes en el canal específico y que no sean de bots
    if message.channel.id == CHANNEL_ID and not message.author.bot:
        # Verificar si se puede enviar notificación
        if can_send_notification():
            content = f"Nuevo mensaje en {message.guild.name} - #{message.channel.name}:\n{message.author}: {message.content}"
            
            # Actualizar el tiempo de la última notificación
            last_notification_time = datetime.now()
            
            # Enviar notificaciones
            send_email(content)
            send_whatsapp(content)
            print(f"✅ Notificación enviada a las {last_notification_time.strftime('%H:%M:%S')}")
        else:
            # Calcular cuánto tiempo falta para la próxima notificación
            next_time = last_notification_time + timedelta(minutes=COOLDOWN_MINUTES)
            remaining = (next_time - datetime.now()).seconds // 60
            print(f"⏳ Mensaje ignorado. Próxima notificación en {remaining} minutos")
    
    await bot.process_commands(message)

def send_email(content):
    try:
        # Configuración mejorada
        subject = "🚨 Nuevo mensaje en Discord!"
        body = f"Subject: {subject}\n\n{content}"
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, body.encode('utf-8'))
        print("✅ Email enviado!")
    except Exception as e:
        print(f"❌ Error en email: {str(e)}")

def send_whatsapp(content):
    try:
        # Acortar mensajes largos (WhatsApp limita a 4096 caracteres)
        if len(content) > 3000:
            content = content[:3000] + "... [mensaje truncado]"
        
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            body=content,
            from_=TWILIO_PHONE,
            to=YOUR_PHONE
        )
        print(f"✅ WhatsApp enviado! SID: {message.sid}")
    except Exception as e:
        print(f"❌ Error en WhatsApp: {str(e)}")

print("=== Variables cargadas ===")
print(f"DISCORD_TOKEN: {bool(DISCORD_TOKEN)}")  # Debe ser True
print(f"CHANNEL_ID: {CHANNEL_ID}")
print(f"EMAIL_FROM: {EMAIL_FROM}")
print(f"TWILIO_SID: {bool(TWILIO_SID)}")


if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))