import discord
from discord.ext import commands
import random
import json
import os

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'vbucks.json'
SHOP_FILE = 'shop.json'

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        vbucks = json.load(f)
else:
    vbucks = {}

if os.path.exists(SHOP_FILE):
    with open(SHOP_FILE, 'r') as f:
        shop = json.load(f)
else:
    shop = {
        "Cool Role": 500,
        "VIP Access": 1000
    }

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(vbucks, f)

def save_shop():
    with open(SHOP_FILE, 'w') as f:
        json.dump(shop, f)

def get_balance(user_id):
    return vbucks.get(str(user_id), 0)

def add_vbucks(user_id, amount):
    user_id = str(user_id)
    vbucks[user_id] = vbucks.get(user_id, 0) + amount
    save_data()

def remove_vbucks(user_id, amount):
    user_id = str(user_id)
    if vbucks.get(user_id, 0) >= amount:
        vbucks[user_id] -= amount
        save_data()
        return True
    return False

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command()
async def balance(ctx):
    amount = get_balance(ctx.author.id)
    await ctx.send(f'{ctx.author.mention}, you have 💸 {amount} V-Bucks!')

@bot.command()
async def earn(ctx):
    amount = random.randint(50, 150)
    add_vbucks(ctx.author.id, amount)
    await ctx.send(f'{ctx.author.mention}, you earned 💸 {amount} V-Bucks!')

@bot.command()
@commands.has_permissions(administrator=True)
async def give(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("Amount must be positive.")
        return
    add_vbucks(member.id, amount)
    await ctx.send(f'{member.mention} received 💸 {amount} V-Bucks from an admin!')

@bot.command()
async def leaderboard(ctx):
    if not vbucks:
        await ctx.send("No V-Bucks data available yet.")
        return
    sorted_users = sorted(vbucks.items(), key=lambda item: item[1], reverse=True)[:10]
    leaderboard_text = "**🏆 V-Buck Leaderboard 🏆**\n"
    for i, (user_id, amount) in enumerate(sorted_users, 1):
        user = await bot.fetch_user(int(user_id))
        leaderboard_text += f"{i}. {user.name} — {amount} V-Bucks\n"
    await ctx.send(leaderboard_text)

@bot.command()
async def shop(ctx):
    if not shop:
        await ctx.send("The shop is empty!")
        return
    shop_text = "**🛍️ V-Buck Shop**\n"
    for item, cost in shop.items():
        shop_text += f"- {item}: {cost} V-Bucks\n"
    await ctx.send(shop_text)

@bot.command()
async def buy(ctx, *, item_name):
    item_name = item_name.strip()
    user_id = str(ctx.author.id)
    guild = ctx.guild

    if item_name not in shop:
        await ctx.send(f"'{item_name}' is not in the shop.")
        return

    cost = shop[item_name]
    if not remove_vbucks(user_id, cost):
        await ctx.send(f"{ctx.author.mention}, you don't have enough V-Bucks to buy **{item_name}**.")
        return

    role = discord.utils.get(guild.roles, name=item_name)
    if role:
        if role in ctx.author.roles:
            await ctx.send(f"{ctx.author.mention}, you already have the **{item_name}** role.")
        else:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention}, you bought **{item_name}** for {cost} V-Bucks and received the role!")
    else:
        await ctx.send(f"{ctx.author.mention}, you bought **{item_name}** for {cost} V-Bucks!")

bot.run('MTM2NzY0NTM5NjY5NjAzOTQyNA.GkdTYY.VHPIY934vvasklRCoC2A__35xI9zGfw5f3k4-E')
