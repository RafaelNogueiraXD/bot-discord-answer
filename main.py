import discord
from discord.ext import commands
from config import load_config_bot_token
import asyncio
from sdk.jarvas import Jarvas

jarvas = Jarvas()

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
@bot.event
async def on_ready():
    print("Bot ready!")

# 'aliases' sao nome variados que a funcao pode ter
@bot.command(aliases=["h", "ola"])
async def hello(ctx):
    await ctx.send(f"Hello there, {ctx.author.mention}!")

def create_embed(ctx, title, description):
    embeded_msg = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )
    embeded_msg.set_footer(text=f"Request by {ctx.author.name}", icon_url=ctx.author.avatar)
    return embeded_msg

@bot.command(name="app") 
async def get_app(ctx, app_name: str): 
    data = jarvas.read_apps() 
    print(app_name)
    app = next((app for app in data['apps'] if app['name'].lower() == app_name.lower()), None) 
    if app: 
        message = f"""
                    Descrição: {app['description']}\n
                    Status: {app['status']}
                    """
        result = create_embed(ctx=ctx, title=app['name'], description=message)
        await ctx.send(embed=result)

    else:
        result = "App não encontrado." 
        await ctx.send(result)


@bot.command(name="apps")
async def all_apps(ctx):
    data = jarvas.read_apps()
    apps = [app for app in data['apps'] if app['name'] != "discord"]
    result = "\n".join(f"{i+1}. {app['name']}" for i, app in enumerate(apps))
    message = await ctx.send(f"Selecione uma aplicação:\n{result}")

    for i in range(len(apps)):
        await message.add_reaction(f"{i+1}\u20E3")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20E3" for i in range(len(apps))]

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Tempo esgotado para seleção.')
    else:
        index = int(reaction.emoji[0]) - 1
        selected_app = apps[index]
        message = f"""
                    Descrição: {selected_app['description']}\n
                    Status: {selected_app['status']}
                    """
        result = create_embed(ctx=ctx, title=selected_app['name'], description=message)
        await ctx.send(embed=result)


    
@bot.command()
async def ping(ctx):
    embeded_msg = discord.Embed(
        title="Ping",
        description="Latency in ms",
        color=discord.Color.blue()
    )
    embeded_msg.add_field(
        name=f"{bot.user.name}'s latency (ms): ", 
        value=f"{round(bot.latency * 1000)}ms", inline=False
    )
    embeded_msg.set_footer(text=f"Resqueted by {ctx.author.name}", icon_url=ctx.author.avatar)
    await ctx.send(embed=embeded_msg)

bot.run(load_config_bot_token())