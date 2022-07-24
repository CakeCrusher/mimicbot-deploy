import os
import discord
from discord.ext import commands
import requests
import pandas as pd
import json
import data_preprocessing
import asyncio
import pdb
from pathlib import Path
import typer
import datetime
import dotenv
dotenv.load_dotenv()


def start_mimic():
    MIMICBOT_TOKEN = os.getenv("DISCORD_API_KEY")
    # CHANNEL = os.getenv("CHANNEL")
    HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
    AMT_OF_CONTEXT = os.getenv("CONTEXT_LENGTH")
    MODEL_ID = os.getenv("MODEL_ID")
    EOS_TOKEN = "<|endoftext|>"
    # members_df = pd.read_csv(str(Path(model_save["data_path"]) / "members.csv"))
    members_df = None

    typer.secho(
        f"({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) Starting MimicBot.", fg=typer.colors.BLUE)

    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True
    bot = commands.Bot(intents=intents, command_prefix="!")

    def messages_into_input(messages, members_df):
        messages_df_columns = ["content", "timestamp", "channel"]
        context_data = [
            [message.content, message.created_at, message.channel.name]
            for message in messages
        ]

        # remove first mention of bot from each message
        for idx, context_data_ins in enumerate(context_data):
            message = context_data_ins[0]
            bot_id_decorated = f"<@{bot.user.id}>"
            split_by_bot_id = message.split(bot_id_decorated)
            start_of_message = split_by_bot_id[0]
            rest_of_message = bot_id_decorated.join(split_by_bot_id[1:])
            new_message = (start_of_message + rest_of_message).strip()
            context_data[idx][0] = new_message

        context_df = pd.DataFrame(
            columns=messages_df_columns, data=context_data)
        context_df = data_preprocessing.clean_df(context_df, members_df)

        return EOS_TOKEN.join(list(context_df["content"])) + EOS_TOKEN

    def query(payload_input):
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
        messages_list = payload_input.split(EOS_TOKEN)[:-1]
        payload = {
            "inputs": {
                "past_user_inputs": messages_list[:-1],
                "generated_responses": [],
                "text": messages_list[-1],
            }
        }
        payload_dump = json.dumps(payload)
        response = requests.request(
            "POST", API_URL, headers=headers, data=payload_dump)
        return json.loads(response.content.decode("utf-8"))

    @bot.event
    async def on_ready():
        typer.secho(f'\n({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) {bot.user} has been activated.',
                    fg=typer.colors.GREEN)

    @bot.event
    async def on_message(message):
        global members_df
        guild = discord.utils.get(bot.guilds, name=message.guild.name)
        data = [[member.id, member.name]
                for member in guild.members] + [[bot.user.id, bot.user.name]]
        members_df = pd.DataFrame(data, columns=["id", "name"])

        if message.author == bot.user:
            return
        # if message is in allowed channel
        channel = message.channel
        # if channel.name == CHANNEL:
        # if bot is mentioned
        if f"<@{bot.user.id}>" in message.content:
            async with channel.typing():
                typer.secho(f"\n({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) {message.author} mentioned me",
                            fg=typer.colors.BLUE)
                context_messages = await channel.history(limit=int(AMT_OF_CONTEXT)).flatten()
                payload_text = messages_into_input(
                    context_messages, members_df)
                typer.echo(
                    f"\n({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) {payload_text}")
                query_res = query(payload_text)
                attempts = 0
                typer.echo(
                    f"\n({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) {query_res}")
                while "error" in query_res.keys() and attempts <= 3:
                    # wait for model to load and try again
                    time_to_load = int(int(query_res["estimated_time"]) * 1.3)
                    typer.secho(
                        f"\n({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) Waiting for model to load. Will take {time_to_load}s", fg=typer.colors.YELLOW)
                    await asyncio.sleep(time_to_load)
                    query_res = query(payload_text)
                    typer.echo(
                        f"\n({datetime.datetime.now().hour}:{datetime.datetime.now().minute}) {query_res}")
                    attempts += 1
                response = query_res["generated_text"]
                await channel.send(response)

    bot.run(MIMICBOT_TOKEN)


start_mimic()
