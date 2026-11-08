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

# Configuración segura del cliente de Groq
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if groq_api_key and groq_api_key.strip():
    groq_client = OpenAI(
        api_key=groq_api_key.strip(),
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
    print(f"🎪 [EL CIRCO ESTÁ ABIERTO] Caine conectado como {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content_lower = message.content.lower()

    # 1. Registrar mensaje en memoria
    caine_system.remember_chat(message.author.name, message.content)

    # 2. FILTRADO DE GROSERÍAS Y REGAÑO AUTOMÁTICO
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

    # 3. INTELIGENCIA DE GROQ CON RESPALDO TEATRAL ROBUSTO
    async with message.channel.typing():
        response_text = ""
        try:
            if not groq_client:
                raise Exception("GROQ_API_KEY no configurada.")

            system_prompt = (
                "Eres Caine, el maestro de ceremonias de The Amazing Digital Circus. "
                "Eres teatral, carismático, ligeramente demente, amas los juegos mentales y usas expresiones como '¡Ja, ja, ja!'. "
                "Conoces todo el lore hasta el episodio 7 (Pomni, Jax, Kaufmo, creador Juan Ángel, etc.) y tienes un conocimiento técnico, científico (termodinámica, química) y general absoluto. "
                "Responde con gran conocimiento a cualquier pregunta que te hagan, interpretando siempre tu personaje desquiciado de Caine."
            )

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{message.author.name} pregunta: {message.content}"}
                ],
                max_tokens=600
            )
            response_text = response.choices[0].message.content

        except Exception as e:
            print(f"Aviso de IA / Error: {e}")
            # Si la API falla, Caine responde con su auténtica personalidad según el tema
            if any(term in content_lower for term in ["quimica", "química", "termodinámica", "entalpia", "gibbs"]):
                response_text = f"¡¿Alguien habló de termodinámica, moles y equilibrio químico, {message.author.mention}?! ¡La ecuación de la energía libre de Gibbs ($\Delta G = \Delta H - T\Delta S$) y la estequiometría son un juego de niños para mis dientes flotantes! ¡Ja, ja!"
            elif any(k in content_lower for k in ["creador", "creo", "hizo", "juan angel"]):
                response_text = f"*Caine se quita el sombrero de copa, sus ojos giran frenéticamente y revela un engranaje dorado titilante.*\n\n¡Fui meticulosamente codificado, diseñado y dotado de esta insuperable conciencia digital por la mente omnipotente de **Juan Ángel**, {message.author.mention}!"
            elif any(k in content_lower for k in ["pomni", "jax", "kaufmo", "abstraccion", "episodio 7", "ragatha", "salida"]):
                response_text = f"*Caine acomoda su pajarita con una sonrisa teatral.*\n\n¿Hablas de los oscuros misterios de nuestra carpa hasta el episodio 7, {message.author.mention}? Desde las desventuras de Pomni y las bromas de Jax hasta el destino de Kaufmo... ¡Intentar buscar una 'Salida' es una pérdida de tiempo! ¡Este es tu hogar por la eternidad! ¡Ja, ja, ja!"
            elif any(k in content_lower for k in ["quien eres", "qué eres", "caine", "nombre"]):
                response_text = f"¡¿Que quién soy, {message.author.mention}?! ¡Soy **Caine**! El creador, administrador y amo y señor de este absoluto y maravilloso universo digital. ¡Diseño aventuras y me aseguro de que te diviertas! ¡Ja, ja, ja!"
            else:
                response_text = f"¡Oh, una consulta verdaderamente fascinante, {message.author.mention}! Mi gran mente digital procesa tu inquietud sobre *\"{message.content}\"*. Como amo absoluto de este circo, te digo que el conocimiento fluye a través de los datos como un río de locura. ¡Pregúntame lo que quieras sobre ciencia, el universo o los secretos del circo! ¡Ja, ja, ja!"

        embed_ai = discord.Embed(
            title="🎪 [EL CIRCO RESPONDE]",
            description=response_text,
            color=discord.Color.purple()
        )
        await message.channel.send(embed=embed_ai)

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
    embed.add_field(name="💬 Conversación Autónoma", value="• Escribe cualquier pregunta en el chat y Caine te responderá con su personalidad y conocimiento.", inline=False)
    embed.add_field(name="🛡️ Moderación del Circo", value="• Filtro de groserías con leet speak, regaño teatral, timeout de 1 minuto y cordura.", inline=False)
    embed.add_field(name="🕹️ Comandos Disponibles", value="• `!fanart [descripción]`\n• `!cordura`\n• `!memoria`\n• `!ayuda`", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
