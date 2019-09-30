#!/usr/bin/python3.6

import random
import asyncio

import emoji
import discord
from discord.ext import commands

from secrets import discord_secret


bot = commands.Bot(command_prefix="!")



# ------ User functions --------
def increase_level(sequence, buttons):
    sequence.append(random.choice(buttons))


def check_against_sequence(real_sequence, user_sequence):
    ''' Checks the user's sequence against the actual sequence.

        Args:
            real_sequence: <list> of correct button presses.
            user_sequence: <list> of user's button presses.

        Returns:
            "continue" if user's sequence is correct *so far*,
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

    return "continue"


def strip_non_emojis(text):
    text = [c for c in text if c in emoji.UNICODE_EMOJI]
    emoji_only_text = ''.join(text)
    return emoji_only_text


# -- User functions (async) ----
async def button_pressed(*, user, button):
    print(user, button)



# ---------- Classes -----------
class Match():
    ''' A given game match of Simón. '''

    def __init__(self, ctx):
        self.ctx = ctx
        self.messages = {}

        # Variables below are initialized only. Their values will be set by
        # async_init.
        self.buttons = ''


    async def async_init(self, ctx, potential_buttons):
        ''' Must be called manually. The regular __init__ doesn't accept any
            async.
        '''
        self.buttons = await self.set_buttons(potential_buttons)


    async def set_buttons(self, potential_buttons):
        ''' Gets the emojis sent to it and uses them if it can. Sets
            self.buttons itself since __init__ won't accept asyncronous code.
        '''
        buttons = strip_non_emojis(potential_buttons)

        if buttons == '':
            await self.send_message(text='No emojis found! Defaulting to normal buttons', section='warning')
            return '🔴💚🔷🍊'

        if len(buttons) > 10:
            await self.send_message(text='Max of ten emojis', section='warning')
            return buttons[:10]

        return buttons


    async def send_message(self, *, text, section):
        _id = await self.ctx.send(text)
        self.messages[section] = _id


    async def append_to_message(self, *, text, section):
        message = self.messages[section]
        await message.edit(content=f'{message.content}{text}')


    async def add_button(self, *, button, section):
        await self.messages[section].add_reaction(button)


    async def add_buttons(self, *, buttons, section):
        for button in buttons:
            await self.add_button(button=button, section=section)


    async def intro_sequence(self):
        await self.send_message(text="Welcome to *Simón!*", section='intro')
        await asyncio.sleep(1)
        await self.append_to_message(text="\nLook at this net:", section='intro')
        await self.add_buttons(buttons=self.buttons, section='intro')



# ---------- Commands ----------
@bot.command()
async def simon(ctx, *, potential_buttons='🔴💚🔷🍊'):

    match = Match(ctx)
    await match.async_init(ctx, potential_buttons)

    await match.intro_sequence()



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
