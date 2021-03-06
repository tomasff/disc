from enum import Enum, unique, auto
from datetime import datetime

import networkx as nx


@unique
class InteractionType(Enum):
    MESSAGE_REACTION = auto()
    MESSAGE_REPLY = auto()
    MESSAGE_MENTION = auto()


class Interaction:
    def __init__(self, user1, user2, recorded_at, type):
        self.user1 = user1
        self.user2 = user2
        self.type = type

        self.recorded_at = recorded_at

    def weight(self, t_now, half_life):
        return 0.5 ** ((t_now - self.recorded_at).total_seconds() / half_life)


class SocialInteractionGraph:
    def __init__(self, name, weights, half_life=172800):
        self.name = name
        self.t_now = datetime.now()
        self.weights = weights
        self.half_life = half_life

        self.graph = nx.Graph(
            name=self.name,
            half_life=self.half_life,
        )

    def _calc_edge_weight(self, interaction):
        return self.weights[interaction.type.name] * interaction.weight(
            self.t_now, self.half_life
        )

    def add_interaction(self, interaction):
        user1, user2 = interaction.user1, interaction.user2

        weight = self._calc_edge_weight(interaction)

        if weight == 0:
            return

        self.graph.add_node(user1)
        self.graph.add_node(user2)

        if not self.graph.has_edge(user1, user2):
            self.graph.add_edge(user1, user2, weight=0)

        self.graph[user1][user2]["weight"] += self._calc_edge_weight(interaction)

    @property
    def edges(self):
        return self.graph.number_of_edges()

    @property
    def nodes(self):
        return self.graph.number_of_nodes()

    def save(self):
        nx.write_gexf(self.graph, f"{self.name}.gexf")
