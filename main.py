#!/usr/bin/python3.6

import random
import asyncio

import emoji
import discord
from discord.ext import commands

from secrets import discord_secret


bot = commands.Bot(command_prefix="!")

buttons = '🔴💚🔷🍊'


# ------ User functions --------
def increase_level(sequence, buttons):
    sequence.append(random.choice(buttons))


def check_against_sequence(real_sequence, user_sequence):
    ''' Checks the user's sequence against the actual sequence.

        Args:

        Returns:
            "continuing" if user's sequence is correct *so far*,
            "passed" if sequences match exactly,
            "failed" if user's sequence does not match.
    '''
    if user_sequence == real_sequence:
        return "passed"

    if len(user_sequence) > len(real_sequence):
        return "failed"

    for real_button, user_button in zip(real_sequence, user_sequence):
        if user_button != real_button:
            return "failed"

    return "continuing"


def strip_non_emojis(text):
    text = [c for c in text if c in emoji.UNICODE_EMOJI]
    emoji_only_text = ''.join(text)
    return emoji_only_text


# -- User functions (async) ----
async def button_pressed(*, user, button):
    print(user, button)



# ---------- Commands ----------
@bot.command()
async def simon(ctx, *, buttons=buttons):

    buttons = strip_non_emojis(buttons)
    if buttons == '':
        await ctx.send('No usable emojis found!')

    string = "Welcome to *Simón!*"
    own_message = await ctx.send(string)

    for button in buttons:
        await own_message.add_reaction(button)



# ----------- Events -----------
@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message

    if message.author.id == bot.user.id:
        await button_pressed(user=user.id, button=reaction)


@bot.event
async def on_reaction_remove(reaction, user):
    message = reaction.message

    if message.author.id == bot.user.id:
        await button_pressed(user=user.id, button=reaction)


if __name__ == '__main__':
    bot.run(discord_secret)
