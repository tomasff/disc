import click
import matplotlib.pyplot as plt

from tqdm import tqdm
from discord import Client, ChannelType, MessageType, NotFound
from .social_graph import SocialInteractionGraph, InteractionType, Interaction


def is_text_or_voice(channel):
    return channel.type == ChannelType.text


class DiscClient(Client):
    def __init__(self, guild, max_messages, half_life, weights):
        super(DiscClient, self).__init__()

        self.guild = guild
        self.max_messages = max_messages

        self.graph = SocialInteractionGraph(
            name=guild,
            weights=weights,
            half_life=half_life,
        )

    async def on_ready(self):
        guild = self.get_guild(self.guild)

        if not guild:
            click.echo("Failed to load the target guild. Cannot collect interactions.")
            return

        channels = list(filter(is_text_or_voice, guild.channels))

        for channel in tqdm(channels, desc="Processing channels"):
            permissions = channel.permissions_for(guild.me)

            if not (permissions.read_message_history and permissions.read_messages):
                continue

            async for message in channel.history(limit=self.max_messages):
                await self.process_message(message)

        click.echo(
            f"Complete! Edges: {self.graph.graph.number_of_edges()}, \
                    Vertices: {self.graph.graph.number_of_nodes()}"
        )

        self.graph.save()
        await self.close()

    async def process_message(self, message):
        if message.type != MessageType.default:
            return

        await self.process_message_reference(message)
        await self.process_message_mentions(message)
        await self.process_message_reactions(message)

    async def process_message_mentions(self, message):
        for user in message.mentions:
            if user == message.author:
                continue

            self.graph.add_interaction(
                Interaction(
                    user1=message.author,
                    user2=user,
                    type=InteractionType.MESSAGE_MENTION,
                    recorded_at=message.created_at,
                )
            )

    async def process_message_reference(self, message):
        if not message.reference:
            return

        referenced_message = await self.get_referenced_message(message.reference)

        if not referenced_message:
            return

        if referenced_message.type != MessageType.default:
            return

        if message.author == referenced_message.author:
            return

        self.graph.add_interaction(
            Interaction(
                user1=message.author,
                user2=referenced_message.author,
                type=InteractionType.MESSAGE_REPLY,
                recorded_at=message.created_at,
            )
        )

    async def get_referenced_message(self, reference):
        if reference.cached_message:
            return reference.cached_message

        try:
            referenced_channel = await self.fetch_channel(reference.channel_id)
            return await referenced_channel.fetch_message(reference.message_id)
        except NotFound:
            return None

    async def process_message_reactions(self, message):
        for reaction in message.reactions:
            async for user in reaction.users():
                if user == message.author:
                    continue

                self.graph.add_interaction(
                    Interaction(
                        user1=message.author,
                        user2=user,
                        recorded_at=message.created_at,
                        type=InteractionType.MESSAGE_REACTION,
                    )
                )
