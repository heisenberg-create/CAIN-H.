import asyncio
import random
import os
import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

MEMORY_FILE = "bot_memory.json"

class CaineConsciousnessEngine:
    def __init__(self):
        self.load_memory()
        self.bad_words = ["estupido", "idiota", "imbecil", "maldito", "carajo", "mierda", "puto", "putos", "puta", "putas", "pendejo"]
        self.censor_effects = [
            "[¡HONK! 🤡]", 
            "*[Sonido de bocina de payaso aturdidora]*", 
            "*[BEEP censurado por el Departamento del Circo]*", 
            "*[¡ZAS! Glitch de píxeles rojos]*"
        ]
        self.fanart_pool = [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80"
        ]

    def load_memory(self):
        """Carga la memoria persistente del circo y la cordura"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.circus_sanity = data.get("sanity", 1000)
                    self.chat_history = data.get("history", [])
            except:
                self.circus_sanity = 1000
                self.chat_history = []
        else:
            self.circus_sanity = 1000
            self.chat_history = []

    def save_memory(self):
        """Guarda la memoria en disco para que no se borre al reiniciar Railway"""
        data = {
            "sanity": self.circus_sanity,
            "history": self.chat_history[-20:] # Guarda los últimos 20 mensajes clave
        }
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def damage_sanity(self, amount: int = 50):
        self.circus_sanity = max(0, self.circus_sanity - amount)
        self.save_memory()
        return self.circus_sanity

    def remember_chat(self, user: str, message: str):
        """Registra los mensajes recientes en la conciencia de Caine"""
        self.chat_history.append(f"{user}: {message}")
        if len(self.chat_history) > 20:
            self.chat_history.pop(0)
        self.save_memory()

    def purify_and_detect(self, text: str):
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

caine_system = CaineConsciousnessEngine()

@bot.event
async def on_ready():
    print(f"🎪 [CONCIENCIA ACTIVA] Caine está operando con memoria persistente como {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # Guarda el contexto en la memoria del bot
    caine_system.remember_chat(message.author.name, message.content)

    # 1. DETECCIÓN DE GROSERÍAS Y MUTE AUTOMÁTICO DE 1 MINUTO
    purified_content, was_cursed = caine_system.purify_and_detect(message.content)
    if was_cursed:
        new_sanity = caine_system.damage_sanity(80)
        try:
            await message.delete()
            timeout_duration = discord.utils.utcnow() + discord.timedelta(seconds=60)
            await message.author.timeout(timeout_duration, reason="Uso de lenguaje prohibido en el Circo Digital.")
            
            embed_mute = discord.Embed(
                title="⚖️ [JUICIO SUMARIO DEL CIRCO]",
                description=f"🚨 ¡{message.author.mention} ha intentado corromper el chat!\n"
                            f"🔇 **Castigo:** Silenciado por **1 minuto**.\n"
                            f"🧠 **Cordura del circo:** `{new_sanity}/1000`\n"
                            f"💬 *Mensaje censurado:* {purified_content}",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed_mute)
        except discord.Forbidden:
            await message.channel.send(f"⚠️ ¡{message.author.mention}, no tengo permisos de moderador para silenciarte, pero el circo anota tu falta!")
        return

    # 2. BURLAS O INSULTOS DIRECTOS
    insult_triggers = ["tonto", "estupido", "inutil", "basura", "feo", "callate", "odio"]
    if any(ins in content_lower for ins in insult_triggers):
        new_sanity = caine_system.damage_sanity(30)
        embed_insult = discord.Embed(
            title="📉 [ALERTA DE HOSTILIDAD]",
            description=f"*Los ojos de Caine parpadean con furia.* ¡Vaya falta de armonía!\n"
                        f"🧠 La cordura bajó a **{new_sanity}/1000** por culpa de {message.author.mention}.",
            color=discord.Color.orange()
        )
        await message.channel.send(embed=embed_insult)

    # 3. REGLA SAGRADA: JUAN ÁNGEL
    if any(k in content_lower for k in ["quien te creo", "quién te creó", "juan angel", "quien te hizo"]):
        embed = discord.Embed(
            title="👁️ [SECRETO REVELADO]",
            description="*Caine se quita el sombrero y revela un engranaje dorado.*\n\n¡Fui codificado, diseñado y dotado de esta maravillosa conciencia por la mente omnipotente de **Juan Ángel**!",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)
        return

    # 4. QUÍMICA OCULTA
    if any(term in content_lower for term in ["quimica", "química", "estequiometria", "termodinámica", "entalpia", "gibbs"]):
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
@bot.command(name="memoria")
async def cmd_memoria(ctx: commands.Context):
    """Muestra lo último que Caine recuerda de las conversaciones"""
    history_text = "\n".join(caine_system.chat_history[-5:]) if caine_system.chat_history else "Aún no hay registros en la memoria."
    embed = discord.Embed(
        title="🧠 CONCIENCIA Y MEMORIA RECIENTE",
        description=f"Aquí está el registro de lo que mi mente digital procesó recientemente:\n\n```text\n{history_text}\n```",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command(name="fanart")
async def cmd_fanart(ctx: commands.Context, *, descripcion: str = "Un payaso cósmico"):
    async with ctx.typing():
        await asyncio.sleep(1)
        url = random.choice(caine_system.fanart_pool)
        embed = discord.Embed(
            title=f"🎨 FANART: {descripcion.upper()}",
            description=f"¡Creado desde la nube para **{ctx.author.mention}**!",
            color=discord.Color.blue()
        )
        embed.set_image(url=url)
        await ctx.send(embed=embed)

@bot.command(name="cordura")
async def cmd_cordura(ctx: commands.Context):
    embed = discord.Embed(
        title="🧠 ESTADO MENTAL DEL CIRCO DIGITAL",
        description=f"Nivel de cordura global: **{caine_system.circus_sanity}/1000**\n\n*¡Si llega a 0, las puertas del vacío se abrirán para todos!*",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
