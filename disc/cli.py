import click
from .discord_client import DiscClient


@click.command()
@click.argument('name')
@click.option('--token', required=True, help='Discord token')
@click.option('--guild', required=True, type=int, help='ID of the guild to build the graph from')
def build(token, guild, name):
    client = DiscClient(guild=guild)
    client.run(token)
