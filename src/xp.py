# xp.py

import discord
from PIL import Image, ImageDraw, ImageFont
import os
import aiohttp
import random
from typing import Optional
from discord import File

ASSETS_PATH = "assets"
FONTS_PATH = "fonts"
TMP_PATH = "tmp"
XP_PER_LVL = 100

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def shadow_tuple(self):
        return (self.x + 1, self.y + 1)

    def as_tuple(self):
        return (self.x, self.y)

IMG_BG = os.path.join(ASSETS_PATH, "bg_rank.png")
IMG_FRAME = os.path.join(ASSETS_PATH, "bg_rank_border_square.png")
IMG_BG2 = os.path.join(ASSETS_PATH, "bg_rank.png")
IMG_FRAME2 = os.path.join(ASSETS_PATH, "bg_rank_border_square.png")
IMG_SM_BAR = os.path.join(ASSETS_PATH, "bg_rank_bar_small.png")
IMG_LG_BAR = os.path.join(ASSETS_PATH, "bg_rank_bar_large.png")
FONT = os.path.join(FONTS_PATH, "Roboto/Roboto-Medium.ttf")
FONT_COLOR = (208, 80, 84)
BACK_COLOR = (82, 31, 33)
USERNAME_POS = Point(90, 8)
LEVEL_POS = Point(90, 63)
RANK_POS = Point(385, 68)
BAR_X = [133, 153, 173, 193, 213, 247, 267, 287, 307, 327]
BAR_Y = 37

xp_data = {}

async def download_avatar(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                with open(filename, 'wb') as f:
                    f.write(data)
                return True
    return False

async def render_level_up_image(user: discord.Member, old_level: int, new_level: int) -> Optional[str]:
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    out_filename = os.path.join(TMP_PATH, f"level_up_{user.id}_{user.guild.id}.png")

    bg = Image.open(IMG_BG2)
    frame = Image.open(IMG_FRAME2)

    bg.paste(frame, (14, 12), frame)

    draw = ImageDraw.Draw(bg)
    font_22 = ImageFont.load_default()

    # Add big text in the middle
    level_text = f"{old_level} -> {new_level}"
    level_width = font_22.getlength(level_text)
    draw.text((bg.width // 2 - level_width // 2, bg.height // 2 - 10), level_text, FONT_COLOR, font=font_22)

    bg.save(out_filename)
    bg.close()
    frame.close()

    return out_filename

async def render_lvl_image(user: discord.Member, username: str, xp: int, rank: int) -> Optional[str]:
    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    lvl = xp // XP_PER_LVL
    bar_num = (10 * (xp - (lvl * XP_PER_LVL))) // XP_PER_LVL

    out_filename = os.path.join(TMP_PATH, f"{user.id}_{user.guild.id}.png")
    avatar_filename = out_filename

    avatar_url = user.display_avatar.url

    success = await download_avatar(avatar_url, avatar_filename)
    if not success:
        return None

    bg = Image.open(IMG_BG)
    avatar = Image.open(avatar_filename).convert("RGBA")
    frame = Image.open(IMG_FRAME)
    small_bar = Image.open(IMG_SM_BAR)
    large_bar = Image.open(IMG_LG_BAR)

    avatar = avatar.resize((68, 68))
    bg.paste(avatar, (16, 14), avatar)
    bg.paste(frame, (14, 12), frame)

    for i in range(bar_num):
        if i % 5 == 4:
            bg.paste(large_bar, (BAR_X[i], BAR_Y), large_bar)
        else:
            bg.paste(small_bar, (BAR_X[i], BAR_Y), small_bar)

    draw = ImageDraw.Draw(bg)
    font_14 = ImageFont.load_default()
    font_22 = ImageFont.load_default()

    draw.text(USERNAME_POS.shadow_tuple(), username, BACK_COLOR, font=font_22)
    draw.text(USERNAME_POS.as_tuple(), username, FONT_COLOR, font=font_22)

    draw.text(LEVEL_POS.shadow_tuple(), f"Level {lvl}", BACK_COLOR, font=font_22)
    draw.text(LEVEL_POS.as_tuple(), f"Level {lvl}", FONT_COLOR, font=font_22)

    rank_text = f"Server Rank : {rank}"
    rank_width = font_14.getlength(rank_text)
    draw.text((RANK_POS.x - rank_width, RANK_POS.y), rank_text, BACK_COLOR, font=font_14)

    bg.save(out_filename)
    bg.close()
    avatar.close()
    frame.close()
    small_bar.close()
    large_bar.close()

    return out_filename

def get_xp(user_id, guild_id):
    return f"{xp_data.get((user_id, guild_id), 0)} XP"

def get_rank(user_id, guild_id):
    sorted_users = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)
    user_rank = next((i+1 for i, ((uid, gid), _) in enumerate(sorted_users) if uid == user_id and gid == guild_id), None)
    return user_rank
