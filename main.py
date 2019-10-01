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



# ---------- Classes -----------
class Match():
    ''' A given game match of Simón. '''

    def __init__(self, ctx):
        self.ctx = ctx
        self.messages = {}
        self.player = ctx.author
        self.turn_no = 1
        self.sequence = ''
        self.user_sequence = ''
        self.status = 'continue'

        self.last_button_press = {'id': 0, 'button': ''}

        # Variables below are initialized only. Their values will be set by
        # async_init.
        self.buttons = str()


    async def async_init(self, ctx, potential_buttons):
        ''' Must be called manually. The regular __init__ doesn't accept any
            async.
        '''
        self.buttons = await self.get_buttons(potential_buttons)


    async def get_buttons(self, potential_buttons):
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
        if section in self.messages.keys():
            _id = await self.messages[section].edit(content=text)
        else:
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


    async def remove_all_messages(self):
        for message in self.messages.values():
            await message.delete()


    # --- Game
    async def button_pressed(self, *, user, button):
        if user == self.player.id:
            button_press_id = self.last_button_press['id'] + 1
            self.last_button_press = {'id': button_press_id, 'button': button}


    async def add_to_sequence(self, sequence):
        sequence += random.choice(self.buttons)
        return sequence

    
    async def perform_turn(self):
        async def wait_and_check_button_press(self):
            last_button_press = self.last_button_press

            while last_button_press == self.last_button_press:
                await asyncio.sleep(0.1)
            else:
                self.user_sequence += self.last_button_press['button'].emoji

            sequence_check = check_against_sequence(self.sequence, self.user_sequence) 

            if sequence_check == 'failed':
                await self.game_over()
            elif sequence_check == 'passed':
                self.user_sequence = ''
                return
            elif sequence_check == 'continue':
                await wait_and_check_button_press(self)


        self.sequence = await self.add_to_sequence(self.sequence)
        await self.send_message(text=f'New sequence: {self.sequence}', section='turn')

        status = await wait_and_check_button_press(self)
        if status == 'failed':
            return status
        else:
            self.turn_no += 1


    async def game_over(self):
        await self.send_message(text=f'Oh No!!! You lost on turn `{self.turn_no}`!', section='loss')
        await asyncio.sleep(.5)
        await self.append_to_message(text="\nShutting down game in a few seconds!", section='loss')
        await asyncio.sleep(3)
        self.status = 'failed'


    async def intro_sequence(self):
        await self.send_message(text="Welcome to *Simón!*", section='intro')
        await asyncio.sleep(1)
        await self.append_to_message(text="\nLook at this net:", section='intro')
        await self.add_buttons(buttons=self.buttons, section='intro')



# ---------- Globals -----------
match = None

# ---------- Commands ----------
@bot.command()
async def simon(ctx, *, potential_buttons='🔴💚🔷🍊'):
    global match

    match = Match(ctx)
    await match.async_init(ctx, potential_buttons)

    await match.intro_sequence()

    while True:
        await match.perform_turn()

        if match.status == 'failed':
            await match.remove_all_messages()

            text = f"Score of: `{str(match.turn_no)}`! Thanks for playing Simón, `{match.player}`!\n🔴💚 To start a new match, type `!simon` 🔷🍊"
            await match.send_message(text=text, section='thanks')
            break



# ----------- Events -----------
@bot.event
async def on_reaction_add(reaction, user):
    global match

    message = reaction.message

    if message.author.id == bot.user.id:
        await match.button_pressed(user=user.id, button=reaction)


@bot.event
async def on_reaction_remove(reaction, user):
    global match

    message = reaction.message

    if message.author.id == bot.user.id:
        await match.button_pressed(user=user.id, button=reaction)


if __name__ == '__main__':
    bot.run(discord_secret)
