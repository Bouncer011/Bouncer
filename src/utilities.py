# utilities.py

import discord
from discord.ext import commands
from custom.bouncer import bouncer_command
from xp import XP_PER_LVL, xp_data, render_lvl_image, get_rank

# ... (other imports and constants)

# Setup functions
async def setup_logging(client):
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

async def update_user_count(guild):
    activity = discord.Activity(name=f"{guild.member_count} members", type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)

# Other utility functions
@bouncer_command
@commands.command()
async def send_giveaway(ctx, prize, winners, duration):
    embed = discord.Embed(title="🎉 **GIVEAWAY** 🎉", description=f"{prize}")
    embed.add_field(name="Winners", value=f"{winners}")
    embed.add_field(name="Ends in", value=f"{duration} minutes")
    msg = await ctx.send(embed=embed)
    
    await msg.add_reaction("🎉")
    
    await sleep(duration * 60)
    
    new_msg = await ctx.channel.fetch_message(msg.id)
    
    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winners = random.sample(users, k=winners)
    
    await ctx.send(f"Congratulations {', '.join(str(w) for w in winners)}!")

# Rank command
@bouncer_command
@commands.command()
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    username = member.display_name
    xp = xp_data.get((member.id, ctx.guild.id), 0)
    rank = get_rank(member.id, ctx.guild.id)
    image_path = await render_lvl_image(member, username, xp, rank)

    if image_path:
        await ctx.send(f"Hello, {member.mention}! Here's your rank!", file=discord.File(image_path))
        os.remove(image_path)

@bouncer_command
@commands.command()  
async def giveaway(ctx, prize, winners, duration):
    await send_giveaway(ctx, prize, winners, duration)

# Config commands
@bouncer_command
@commands.command()
async def set_status(ctx, status_type, *, status_text):
    types = {
        'playing': discord.Game,
        'streaming': discord.Streaming,
        'listening': discord.ActivityType.listening,
        'watching': discord.ActivityType.watching,
    }
    activity_type = types.get(status_type.lower())
    
    if activity_type:
        activity = activity_type(name=status_text)
        await client.change_presence(activity=activity)
        await ctx.send(f"Status set to {status_type.capitalize()}: {status_text}")
    else:
        await ctx.send("Invalid status type. Use playing, streaming, listening, or watching.")

@bouncer_command
@commands.command()
async def set_prefix(ctx, new_prefix):
    # Assuming you have a global variable `bot` defined
    bot.command_prefix = new_prefix
    await ctx.send(f"Prefix set to: {new_prefix}")
