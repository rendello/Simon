#!/usr/bin/python3.6

import discord
from discord.ext import commands

from secrets import discord_secret

bot = commands.Bot(command_prefix="!")


@bot.command()
async def simon(ctx):
    string = "Welcome to *Simón!*"
    await ctx.add_reaction('\:green_heart:')
    await ctx.send(string)

bot.run(discord_secret)
