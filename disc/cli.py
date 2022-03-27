import click
from .discord_client import DiscClient


@click.command()
@click.argument('name')
@click.option('--token', required=True, help='Discord token')
@click.option('--guild', required=True, type=int, help='ID of the guild to build the graph from')
@click.option('--max_messages', required=True, type=int)
def build(token, guild, max_messages, name):
    client = DiscClient(guild=guild, max_messages=max_messages)
    client.run(token)
