#!/usr/bin/python3.6

import discord
from discord.ext import commands

from secrets import discord_secret

bot = commands.Bot(command_prefix="!")


@bot.command()
async def simon(ctx):
    string = "Welcome to *Simón!*"
    await ctx.message.add_reaction('💕')
    await ctx.send(string)


@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message

    if message.author.id == bot.user.id:
        await message.channel.send(reaction)


bot.run(discord_secret)
