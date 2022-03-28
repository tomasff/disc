import click
from .discord_client import DiscClient


@click.command()
@click.argument("name")
@click.option("--token", required=True, help="Discord token")
@click.option(
    "--guild", required=True, type=int, help="ID of the guild to build the graph from"
)
@click.option(
    "--half-life",
    type=int,
    help="Half-life to be used to calculate the edges' weight",
)
@click.option(
    "--max-messages",
    required=True,
    type=int,
    help="Maximum number of messages to be fetched per guild channel",
)
def build(token, guild, max_messages, half_life, name):
    client = DiscClient(
        guild=guild,
        max_messages=max_messages,
        half_life=half_life
    )

    client.run(token)
