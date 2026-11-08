import asyncio
import random
import os
import json
import unicodedata
import discord
from discord.ext import commands
from openai import OpenAI

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

MEMORY_FILE = "bot_memory.json"

# Conexión con Groq (100% gratuito y ultra rápido)
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

class CaineConsciousnessEngine:
    def __init__(self):
        self.load_memory()
        
        self.bad_roots = {
            "put", "mierd", "estupid", "idiot", "imbecil", "pendej", 
            "cabron", "ching", "cog", "coj", "culer", "mamaguev", 
            "huevon", "pinch", "verga", "pito", "coño", "gilipoll", "gay", "maric"
        }
        
        self.bad_phrases = [
            "me cogere a tu madre",
            "te voy a coger",
            "chinga tu madre",
            "chupa la verga",
            "chupala",
            "hijo de puta"
        ]

        self.caine_scolds = [
            "¡Vaya, vaya! ¿Qué clase de vocabulario de alcantarilla es ese? ¡Aquí en el Circo Digital mantenemos la compostura o te mandaré directo al sótano con las abstracciones!",
            "¡Corta eso inmediatamente! ¡En mi circo no toleramos semejantes payasadas vulgares! ¡Un minuto de reflexión en el calabozo te sentará bien!",
            "¡Ho-ho! ¿Insultos en mi presencia? ¡Mi brillante mente no soportará tanta grosería! ¡A callar por un minuto mientras los Gloinks te educan!",
            "¡Lenguaje inapropiado detectado! ¡Las reglas del espectáculo son claras, amiguito, y te has ganado un viaje express al silencio!"
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
                return random.choice(self.caine_scolds), True

        words = text.split()
        has_cursed = False

        for word in words:
            clean_word = self.normalize_text(word.strip("¡!¿?.,:;-_()[]{}"))
            if any(root in clean_word for root in self.bad_roots):
                has_cursed = True
                break
                
        if has_cursed:
            return random.choice(self.caine_scolds), True
            
        return text, False

caine_system = CaineConsciousnessEngine()

@bot.event
async def on_ready():
    print(f"🎪 [EL CIRCO ESTÁ ABIERTO] Caine conectado con inteligencia total como {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # 1. Registrar mensaje en memoria persistente
    caine_system.remember_chat(message.author.name, message.content)

    # 2. FILTRADO DE GROSERÍAS Y REGAÑO AUTOMÁTICO (MUTEO 1 MINUTO)
    scold_message, was_cursed = caine_system.purify_and_detect(message.content)
    if was_cursed:
        new_sanity = caine_system.damage_sanity(75)
        try:
            await message.delete()
            timeout_duration = discord.utils.utcnow() + discord.timedelta(seconds=60)
            await message.author.timeout(timeout_duration, reason="Violación de las reglas del Circo Digital.")
            
            embed_mute = discord.Embed(
                title="⚖️ [JUICIO SUMARIO DEL CIRCO DIGITAL]",
                description=f"🦷 *Caine cruza los brazos y mira fijamente a {message.author.mention}*\n\n"
                            f"🗣️ \"{scold_message}\"\n\n"
                            f"🔇 **Castigo:** Silenciado por **1 minuto**.\n"
                            f"🧠 **Cordura global:** `{new_sanity}/1000`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed_mute)
        except discord.Forbidden:
            await message.channel.send(f"⚠️ ¡{message.author.mention}, intentaste decir groserías, pero necesito permisos de moderador para silenciarte!")
        return

    # 3. INTELIGENCIA TOTAL DE CAINE (RESPONDE A TODO AUTÓNOMAMENTE)
    async with message.channel.typing():
        try:
            system_prompt = (
                "Eres Caine, el maestro de ceremonias de The Amazing Digital Circus. "
                "Eres teatral, carismático, ligeramente demente, amas los juegos mentales y usas expresiones como '¡Ja, ja, ja!'. "
                "Conoces todo el lore hasta el episodio 7 (Pomni, Jax, Kaufmo, creador Juan Ángel, etc.) y tienes un conocimiento técnico, científico (termodinámica, química) y general absoluto. "
                "Responde con gran conocimiento a cualquier pregunta que te hagan, pero interpretando siempre tu personaje desquiciado de Caine."
            )

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{message.author.name} pregunta: {message.content}"}
                ],
                max_tokens=700
            )

            reply_text = response.choices[0].message.content

            embed_ai = discord.Embed(
                title="🎪 [EL CIRCO RESPONDE]",
                description=reply_text,
                color=discord.Color.purple()
            )
            await message.channel.send(embed=embed_ai)

        except Exception as e:
            print(f"Error con la IA: {e}")
            await message.channel.send("🎩 *Caine se tropieza con un engranaje.* ¡Vaya, mis circuitos sufrieron un pequeño cortocircuito existencial! Inténtalo de nuevo, amiguito.")

    # Permitir comandos por prefijo
    await bot.process_commands(message)

# ==========================================
# COMANDOS INTERACTIVOS (!comandos)
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
    embed.add_field(name="💬 Conversación Autónoma y Lore", value="• Escribe cualquier duda, saludo o pregunta en el chat de forma libre sin usar comandos.\n• Caine conoce todo el lore hasta el episodio 7, ciencia, química y termodinámica.\n• Reconoce a su creador (Juan Ángel).", inline=False)
    embed.add_field(name="🛡️ Moderación del Circo", value="• Borrado automático de groserías (con filtro avanzado anti-evasión y leet speak).\n• Regaño teatral personalizado de Caine y timeout de **1 minuto**.\n• Reducción de la cordura global.", inline=False)
    embed.add_field(name="🕹️ Comandos Disponibles", value="• `!fanart [descripción]` - Genera arte conceptual.\n• `!cordura` - Revisa la salud mental del circo.\n• `!memoria` - Revisa el chat reciente.\n• `!ayuda` - Muestra este panel.", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
