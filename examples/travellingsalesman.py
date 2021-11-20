import treesearchsolverpy

import json
import math
from functools import total_ordering


class Location:
    id = -1
    x = 0
    y = 0


class Instance:

    def __init__(self, filepath=None):
        self.locations = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["xs"],
                        data["ys"])
                for (x, y) in locations:
                    self.add_location(x, y)

    def add_location(self, x, y):
        location = Location()
        location.id = len(self.locations)
        location.x = x
        location.y = y
        self.locations.append(location)

    def distance(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def write(self, filepath):
        data = {"xs": [location.x for location in self.locations],
                "ys": [location.y for location in self.locations]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        with open(filepath) as json_file:
            n = len(self.locations)
            data = json.load(json_file)
            locations = data["locations"]
            length = 0
            location_pred_id = 0
            for location_id in data["locations"] + [0]:
                length += self.distance(location_pred_id, location_id)
                location_pred_id = location_id
            number_of_duplicates = len(locations) - len(set(locations))
            is_feasible = (
                    (number_of_duplicates == 0)
                    and len(locations) == n - 1
                    and 0 not in locations)
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"Number of locations: {len(locations) + 1} / {n}")
            print(f"Feasible: {is_feasible}")
            print(f"Length: {length}")
            return (is_feasible, length)


class BranchingScheme:
    """An elementary branching scheme for the Travelling Salesman Problem."""

    @total_ordering
    class Node:
        """Node class.

        Attributes
        ----------

        id : int
            Unique id, given by the BranchingScheme.
        father : Node or None
            father of the nodes, None if it is the root node.
        visited : int
            bitset implemented with an int to store the visited
            locations of the partial tour.
            To determine if location j has been visited::
                (node.visited >> j) & 1
            To add location j to the visited locations:
                node.visited += (1 << j)
        number_of_locations : int
            Number of visited locations in the partial tour.
        j : int
            Last visited location.
        length : int
            length of the partial tour (without going back to location 0).
        guide : float
            guide of the node.
        next_child_pos : int
            position of the next child to generate.

        """

        id = None
        father = None
        visited = None
        number_of_locations = None
        j = None
        length = None
        guide = None
        next_child_pos = 0

        def __lt__(self, other):
            if self.guide != other.guide:
                return self.guide < other.guide
            return self.id < other.id

    def __init__(self, instance):
        self.instance = instance
        self.id = 0

    def root(self):
        # The root node contains only location 0.
        node = self.Node()
        node.father = None
        node.visited = (1 << 0)
        node.number_of_locations = 1
        node.j = 0
        node.length = 0
        node.guide = 0
        node.id = self.id
        self.id += 1
        return node

    def next_child(self, father):
        # Find the next location to add to the partial tour.
        j_next = father.next_child_pos
        # Update node.next_child_pos.
        father.next_child_pos += 1
        # If this location has already been visited, return.
        if (father.visited >> j_next) & 1:
            return None
        # Build child node.
        child = self.Node()
        child.father = father
        child.visited = father.visited + (1 << j_next)
        child.number_of_locations = father.number_of_locations + 1
        child.j = j_next
        child.length = father.length + self.instance.distance(father.j, j_next)
        child.guide = child.length
        child.id = self.id
        self.id += 1
        return child

    def infertile(self, node):
        return node.next_child_pos == len(self.instance.locations)

    def leaf(self, node):
        return node.number_of_locations == len(self.instance.locations)

    def bound(self, node_1, node_2):
        # Check if node_2 is feasible.
        if node_2.number_of_locations < len(self.instance.locations):
            return False
        d2 = node_2.length + self.instance.distance(node_2.j, 0)
        return node_1.length >= d2

    # Solution pool.

    def better(self, node_1, node_2):
        # Check if node_1 is feasible.
        if node_1.number_of_locations < len(self.instance.locations):
            return False
        # Check if node_2 is feasible.
        if node_2.number_of_locations < len(self.instance.locations):
            return True
        # Compute the objective value of node_1.
        d1 = node_1.length + self.instance.distance(node_1.j, 0)
        # Compute the objective value of node_2.
        d2 = node_2.length + self.instance.distance(node_2.j, 0)
        return d1 < d2

    def equals(self, node_1, node_2):
        return False

    # Dominances.

    def comparable(self, node):
        return True

    class Bucket:

        def __init__(self, node):
            self.node = node

        def __hash__(self):
            return hash((self.node.j, self.node.visited))

        def __eq__(self, other):
            return (
                    # Same last location.
                    self.node.j == other.node.j
                    # Same visited locations.
                    and self.node.visited == other.node.visited)

    def dominates(self, node_1, node_2):
        if node_1.length <= node_2.length:
            return True
        return False

    # Outputs.

    def display(self, node):
        # Check if node is feasible.
        if node.number_of_locations < len(self.instance.locations):
            return ""
        # Compute the objective value of node.
        d = node.length + self.instance.distance(node.j, 0)
        return str(d)

    def to_solution(self, node):
        locations = []
        node_tmp = node
        while node_tmp.father is not None:
            locations.append(node_tmp.j)
            node_tmp = node_tmp.father
        locations.reverse()
        return locations


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="iterative_beam_search",
            help='')
    parser.add_argument(
            "-i", "--instance",
            type=str,
            help='')
    parser.add_argument(
            "-c", "--certificate",
            type=str,
            default=None,
            help='')

    args = parser.parse_args()

    if args.algorithm == "generator":
        import random
        random.seed(0)
        for number_of_locations in range(1, 101):
            instance = Instance()
            total_weight = 0
            for location_id in range(number_of_locations):
                x = random.randint(0, 1000)
                y = random.randint(0, 1000)
                instance.add_location(x, y)
            instance.write(
                    args.instance + "_" + str(number_of_locations) + ".json")

    elif args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)

    else:
        instance = Instance(args.instance)
        branching_scheme = BranchingScheme(instance)
        if args.algorithm == "greedy":
            output = treesearchsolverpy.greedy(
                    branching_scheme)
        elif args.algorithm == "best_first_search":
            output = treesearchsolverpy.best_first_search(
                    branching_scheme,
                    time_limit=30)
        elif args.algorithm == "iterative_beam_search":
            output = treesearchsolverpy.iterative_beam_search(
                    branching_scheme,
                    time_limit=30)
        solution = branching_scheme.to_solution(output["solution_pool"].best)
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            instance.check(args.certificate)
