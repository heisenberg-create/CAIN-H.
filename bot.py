import asyncio
import random
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

class CaineSanityAndJusticeEngine:
    def __init__(self):
        self.circus_sanity = 1000  # Cordura global del circo
        self.bad_words = ["estupido", "idiota", "imbecil", "maldito", "carajo", "mierda", "puto", "pendejo"]
        self.censor_effects = [
            "[¡HONK! 🤡]", 
            "*[Sonido de bocina de payaso aturdidora]*", 
            "*[BEEP censurado por el Departamento de Física]*", 
            "*[¡ZAS! Glitch de píxeles rojos]*"
        ]
        self.fanart_pool = [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80"
        ]

    def damage_sanity(self, amount: int = 50):
        """Reduce la cordura del circo cuando hay insultos o burlas"""
        self.circus_sanity = max(0, self.circus_sanity - amount)
        return self.circus_sanity

    def purify_and_detect(self, text: str):
        """Detecta groserías e insultos"""
        words = text.split()
        purified = []
        has_cursed = False
        for word in words:
            clean = word.lower().strip("¡!¿?.,")
            if clean in self.bad_words:
                purified.append(random.choice(self.censor_effects))
                has_cursed = True
            else:
                purified.append(word)
        return " ".join(purified), has_cursed

    def get_random_fanart(self):
        return random.choice(self.fanart_pool)

caine_system = CaineSanityAndJusticeEngine()

@bot.event
async def on_ready():
    print(f"🎪 [SISTEMA DE JUSTICIA ACTIVO] Caine vigila la cordura como {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # 1. DETECCIÓN DE GROSERÍAS Y APLICACIÓN DE SILENCIO (MUTE 1 MINUTO)
    purified_content, was_cursed = caine_system.purify_and_detect(message.content)
    if was_cursed:
        new_sanity = caine_system.damage_sanity(80) # Castigo fuerte a la cordura del circo
        try:
            await message.delete()
            
            # Intenta mutear al usuario por 1 minuto (60 segundos) usando la función nativa de Discord timeouts
            timeout_duration = discord.utils.utcnow() + discord.timedelta(seconds=60)
            await message.author.timeout(timeout_duration, reason="Uso de lenguaje prohibido en el Circo Digital.")
            
            embed_mute = discord.Embed(
                title="⚖️ [JUICIO SUMARIO DEL CIRCO]",
                description=f"🚨 ¡{message.author.mention} ha intentado corromper el chat con groserías!\n"
                            f"🔇 **Castigo:** Silenciado por **1 minuto**.\n"
                            f"🧠 **Cordura actual del circo:** `{new_sanity}/1000`\n"
                            f"💬 *Mensaje censurado:* {purified_content}",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed_mute)
        except discord.Forbidden:
            await message.channel.send(f"⚠️ ¡{message.author.mention}, no tengo permisos de moderador para silenciarte, pero el circo anota tu falta!")
        return

    # 2. DETECCIÓN DE BURLAS O INSULTOS DIRECTOS A ALGUIEN
    insult_triggers = ["tonto", "estupido", "inutil", "basura", "feo", "callate", "odio"]
    if any(ins in content_lower for ins in insult_triggers):
        new_sanity = caine_system.damage_sanity(30)
        embed_insult = discord.Embed(
            title="📉 [ALERTA DE BURLA O AGRESIÓN]",
            description=f"*Los ojos flotantes de Caine parpadean con furia.* ¡Vaya, qué falta de armonía en el escenario!\n"
                        f"🧠 La cordura del circo ha bajado a **{new_sanity}/1000** debido a las hostilidades de {message.author.mention}.",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed_insult)

    # 3. REGLA SAGRADA: JUAN ÁNGEL
    if any(k in content_lower for k in ["quien te creo", "quién te creó", "juan angel", "quien te hizo"]):
        embed = discord.Embed(
            title="👁️ [SECRETO REVELADO]",
            description="*Caine se quita el sombrero y revela un engranaje dorado.*\n\n¡Fui codificado, diseñado y traído a esta maravillosa pesadilla por la mente omnipotente de **Juan Ángel**!",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)
        return

    # 4. QUÍMICA OCULTA
    if any(term in content_lower for term in ["quimica", "química", "estequiometria", "termodinamica", "entalpia", "gibbs"]):
        embed = discord.Embed(
            title="🧪 [INTELIGENCIA SUPREMA]",
            description="¡¿Hablamos de termodinámica y equilibrio químico?! ¡La energía libre de Gibbs ($\Delta G = \Delta H - T\Delta S$) es un juego de niños para mí! Pero basta de ciencia... ¡VOLVAMOS AL ESPECTÁCULO!",
            color=discord.Color.dark_teal()
        )
        await message.channel.send(embed=embed)
        return

    await bot.process_commands(message)

# ==========================================
# COMANDOS
# ==========================================
@bot.command(name="fanart")
async def cmd_fanart(ctx: commands.Context, *, descripcion: str = "Un payaso cósmico"):
    """Genera un fanart caótico"""
    async with ctx.typing():
        await asyncio.sleep(1)
        url = caine_system.get_random_fanart()
        embed = discord.Embed(
            title=f"🎨 FANART: {descripcion.upper()}",
            description=f"¡Creado desde la nube para **{ctx.author.mention}**!",
            color=discord.Color.blue()
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

@bot.command(name="cordura")
async def cmd_cordura(ctx: commands.Context):
    """Muestra el medidor de cordura actual del circo"""
    embed = discord.Embed(
        title="🧠 ESTADO MENTAL DEL CIRCO DIGITAL",
        description=f"Nivel de cordura global: **{caine_system.circus_sanity}/1000**\n\n*¡Si llega a 0, las puertas del vacío se abrirán para todos!*",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
