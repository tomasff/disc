import click

from .social_graph import SocialInteractionGraph, InteractionType
from .discord_client import DiscClient

INTERACTION_CHOICES = InteractionType.__members__
DEFAULT_WEIGHTS = {type: 1 for type in InteractionType.__members__}


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
    default=172800,
)
@click.option(
    "--max-messages",
    required=True,
    type=int,
    help="Maximum number of messages to be fetched per guild channel",
)
@click.option(
    "--weight",
    "-w",
    nargs=2,
    type=click.Tuple([click.Choice(INTERACTION_CHOICES), float]),
    multiple=True,
    help="Configures the weight for a given interaction",
)
def build(token, guild, max_messages, half_life, weight, name):
    weights = DEFAULT_WEIGHTS | dict(weight)

    graph = SocialInteractionGraph(
        name=name,
        weights=weights,
        half_life=half_life,
    )

    client = DiscClient(guild=guild, max_messages=max_messages, graph=graph)
    client.run(token)

    click.echo(
        f"Complete! Edges: {graph.number_of_edges()}, "
        f"Vertices: {graph.number_of_nodes()}"
    )

    graph.save()
