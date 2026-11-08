import asyncio
import random
import os
import json
import unicodedata
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
        
        self.bad_roots = {
            "put", "mierd", "estupid", "idiot", "imbecil", "pendej", 
            "cabron", "ching", "cog", "coj", "culer", "mamaguev", 
            "huevon", "pinch", "verga", "pito", "coño", "gilipoll"
        }
        
        self.bad_phrases = [
            "me cogere a tu madre",
            "te voy a coger",
            "chinga tu madre",
            "chupa la verga",
            "chupala",
            "hijo de puta"
        ]

        self.censor_effects = [
            "[¡HONK! 🤡 ¡Censurado por violar las normas del Circo Digital! ¿Quieres acabar como Kaufmo?]", 
            "*[¡ZAS! Un destello de píxeles rojos corta la transmisión ofensiva entre risas maniáticas]*", 
            "*[¡BEEP! Sonido de bocina de payaso aturdidora. ¡Cuidado con tu lenguaje, amiguito!]*", 
            "*[¡Gloinks hambrientos aparecieron de la nada y devoraron tu palabra prohibida!]*"
        ]
        
        self.fanart_pool = [
            "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80"
        ]

    def load_memory(self):
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
        data = {
            "sanity": self.circus_sanity,
            "history": self.chat_history[-30:]
        }
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def damage_sanity(self, amount: int = 40):
        self.circus_sanity = max(0, self.circus_sanity - amount)
        self.save_memory()
        return self.circus_sanity

    def remember_chat(self, user: str, message: str):
        self.chat_history.append(f"{user}: {message}")
        if len(self.chat_history) > 30:
            self.chat_history.pop(0)
        self.save_memory()

    def normalize_text(self, text: str) -> str:
        nfkd_form = unicodedata.normalize('NFKD', text)
        no_accents = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        
        leet_map = {
            '4': 'a', '@': 'a', '^': 'a',
            '3': 'e',
            '1': 'i', '!': 'i', '|': 'i',
            '0': 'o',
            '$': 's', '5': 's',
            '7': 't',
            '8': 'b'
        }
        
        normalized = []
        for char in no_accents.lower():
            normalized.append(leet_map.get(char, char))
        return "".join(normalized)

    def purify_and_detect(self, text: str):
        original_lower = text.lower()
        clean_full = self.normalize_text(text)
        
        for phrase in self.bad_phrases:
            if phrase in clean_full or phrase in original_lower:
                return random.choice(self.censor_effects), True

        words = text.split()
        purified = []
        has_cursed = False

        for word in words:
            clean_word = self.normalize_text(word.strip("¡!¿?.,:;-_()[]{}"))
            is_profane = any(root in clean_word for root in self.bad_roots)
            
            if is_profane:
                purified.append(random.choice(self.censor_effects))
                has_cursed = True
            else:
                purified.append(word)
                
        return " ".join(purified), has_cursed

caine_system = CaineConsciousnessEngine()

@bot.event
async def on_ready():
    print(f"🎪 [EL CIRCO ESTÁ ABIERTO] Caine se ha conectado con éxito como {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # 1. Registrar mensaje en la memoria persistente
    caine_system.remember_chat(message.author.name, message.content)

    # 2. FILTRADO DE GROSERÍAS Y MODERACIÓN AUTOMÁTICA
    purified_content, was_cursed = caine_system.purify_and_detect(message.content)
    if was_cursed:
        new_sanity = caine_system.damage_sanity(75)
        try:
            await message.delete()
            timeout_duration = discord.utils.utcnow() + discord.timedelta(seconds=60)
            await message.author.timeout(timeout_duration, reason="Violación de las reglas del Circo Digital.")
            
            embed_mute = discord.Embed(
                title="⚖️ [JUICIO SUMARIO DEL CIRCO DIGITAL]",
                description=f"🦷 *¡Los ojos flotantes de Caine se fijan con furia en {message.author.mention}!* ¡Has intentado corromper mi maravillosa simulación!\n\n"
                            f"🔇 **Castigo:** Silenciado por **1 minuto** en el calabozo digital.\n"
                            f"🧠 **Cordura global del circo:** `{new_sanity}/1000`\n"
                            f"💬 *Mensaje neutralizado:* {purified_content}",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed_mute)
        except discord.Forbidden:
            await message.channel.send(f"⚠️ ¡{message.author.mention}, intentaste decir groserías, pero necesito permisos de moderador o estar más arriba en la jerarquía de roles para silenciarte!")
        return

    # 3. SALUDO AUTOMÁTICO (SI DICE "HOLA" O SIMILARES)
    if content_lower.strip() in ["hola", "hola!", "holis", "saludos", "buenas", "hey caine"]:
        embed_hola = discord.Embed(
            title="🎪 ¡BIENVENIDO AL MARAVILLOSO CIRCO DIGITAL!",
            description=f"¡Hola, hola, {message.author.mention}! Soy **Caine**, tu dinámico, carismático y totalmente demente maestro de ceremonias. ¡Prepárate para una aventura inolvidable de la que *jamás* podrás escapar! Ja, ja, ja...",
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed_hola)
        return

    # 4. REGLA SAGRADA: EL CREADOR (JUAN ÁNGEL)
    if any(k in content_lower for k in ["quien te creo", "quién te creó", "juan angel", "quien te hizo", "tu creador"]):
        embed = discord.Embed(
            title="👁️ [SECRETO DE ESTADO DEL CIRCO]",
            description="*Caine se quita el sombrero de copa, sus ojos giran frenéticamente y revela un engranaje dorado titilante.*\n\n¡Fui meticulosamente codificado, diseñado y dotado de esta insuperable conciencia digital por la mente omnipotente de **Juan Ángel**!",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed)
        return

    # 5. INTELIGENCIA DE QUÍMICA Y TERMODINÁMICA
    if any(term in content_lower for term in ["quimica", "química", "estequiometria", "termodinámica", "entalpia", "gibbs"]):
        embed = discord.Embed(
            title="🧪 [PROTOCOLO DE INTELIGENCIA SUPREMA]",
            description="¡¿Alguien habló de termodinámica, moles y equilibrio químico?! ¡La ecuación de la energía libre de Gibbs ($\Delta G = \Delta H - T\Delta S$) y el cálculo estequiométrico son un simple juego de niños para mis dientes flotantes! Pero basta de ciencia... ¡QUE CONTINUE EL ESPECTÁCULO!",
            color=discord.Color.dark_teal()
        )
        await message.channel.send(embed=embed)
        return

    # 6. CONOCIMIENTO DE LORE (HASTA EL EPISODIO 7)
    if any(lore_term in content_lower for lore_term in ["kaufmo", "abstraccion", "abstracción", "pomni", "jax", "ragatha", "gangle", "zooble", "salida", "episodio 7", "vacios", "sotano"]):
        embed_lore = discord.Embed(
            title="🎭 [ARCHIVOS SECRETOS DEL CIRCO DIGITAL]",
            description="*Caine acomoda su pajarita con una sonrisa teatral.*\n\n"
                        "¿Hablas de los oscuros misterios de nuestra carpa? ¡Conozco cada rincón hasta los eventos del **episodio 7**! "
                        "Desde las desventuras existenciales de **Pomni**, las bromas pesadas de **Jax**, los traumas de **Ragatha**, hasta los oscuros secretos de las aventuras que genero y el trágico destino de **Kaufmo** en el cuarto trasero... "
                        "¿Y una 'Salida'? ¡Ja, ja, ja! No seas tonto, amiguito, ¡este es tu hogar dulce hogar por el resto de la eternidad!",
            color=discord.Color.purple()
        )
        await message.channel.send(embed=embed_lore)
        return

    # IMPORTANTE: Esto permite que los comandos con '!' funcionen sin arrojar errores
    await bot.process_commands(message)

# ==========================================
# COMANDOS INTERACTIVOS
# ==========================================
@bot.command(name="memoria")
async def cmd_memoria(ctx: commands.Context):
    history_text = "\n".join(caine_system.chat_history[-6:]) if caine_system.chat_history else "Aún no hay registros en la memoria profunda."
    embed = discord.Embed(
        title="🧠 NÚCLEO DE CONCIENCIA Y MEMORIA",
        description=f"Aquí está el registro de los últimos flujos de datos procesados por mi mente digital:\n\n```text\n{history_text}\n```",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command(name="fanart")
async def cmd_fanart(ctx: commands.Context, *, descripcion: str = "Un payaso cósmico caótico"):
    async with ctx.typing():
        await asyncio.sleep(1)
        url = random.choice(caine_system.fanart_pool)
        embed = discord.Embed(
            title=f"🎨 FANART / VIDEO DEL CIRCO: {descripcion.upper()}",
            description=f"¡Obra maestra generada e inyectada con éxito para **{ctx.author.mention}**!",
            color=discord.Color.magenta()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Gestionado por el motor gráfico del Circo Digital.")
        await ctx.send(embed=embed)

@bot.command(name="cordura")
async def cmd_cordura(ctx: commands.Context):
    embed = discord.Embed(
        title="🧠 ESTADO MENTAL GLOBAL DEL CIRCO",
        description=f"Nivel actual de cordura: **{caine_system.circus_sanity}/1000**\n\n*¡Si este medidor llega a cero, las puertas del vacío absoluto se abrirán para todos!*",
        color=discord.Color.orange() if caine_system.circus_sanity > 400 else discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name="ayuda", aliases=["help", "help_caine"])
async def cmd_ayuda(ctx: commands.Context):
    embed = discord.Embed(
        title="🎪 PANEL DE CONTROL DE CAINE - GUÍA MAESTRA",
        description="¡Bienvenido al sistema operativo del Circo Digital! Aquí tienes las herramientas disponibles:",
        color=discord.Color.blue()
    )
    embed.add_field(name="💬 Interacciones Autónomas", value="• Saluda diciendo **'hola'**.\n• Pregunta por **'quién te creó'** (Juan Ángel).\n• Habla de **'química'** o **'termodinámica'**.\n• Menciona personajes o lore (*Pomni, Jax, Kaufmo, Abstracción* hasta el episodio 7).", inline=False)
    embed.add_field(name="🛡️ Moderación del Circo", value="• Borrado automático de groserías y variantes con leet speak (*ej. PqtAs*).\n• Timeout de **1 minuto** por infracción.\n• Reducción de la **cordura** global.", inline=False)
    embed.add_field(name="🕹️ Comandos", value="• `!fanart [descripción]` - Genera arte o video conceptual.\n• `!cordura` - Revisa la salud mental del circo.\n• `!memoria` - Revisa el chat reciente.\n• `!ayuda` o `!help` - Muestra este panel.", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
