import time


class SolutionPool:

    def __init__(self, branching_scheme, maximum_size=1):
        self.branching_scheme = branching_scheme
        self.maximum_size = maximum_size
        root = branching_scheme.root()
        self.best = root
        self.worst = root
        self.solutions = [root]

    def add(self, node):
        # If the new solution is worse than the worst solution of the pool,
        # don't add it and stop.
        if len(self.solutions) >= self.maximum_size:
            if not self.branching_scheme.better(node, self.worst):
                return False
        # If the new solution is already in the pool, don't add it and stop.
        for solution in self.solutions:
            if self.branching_scheme.equals(node, solution):
                return False
        # Add the new solution to solutions.
        self.solutions.append(node)
        # Update best solution.
        if self.branching_scheme.better(node, self.best):
            self.best = node
        # Check the size of the solution pool.
        if len(self.solutions) > self.maximum_size:
            # Remove worst solution.
            i = 0
            while i < len(self.solutions):
                if self.solutions[i] == self.worst:
                    self.solutions[i] = self.solutions[-1]
                    self.solutions.pop()
                    break
                else:
                    i += 1
            # Compute new worst solutions.
            self.worst = self.solutions[0]
            for solution in self.solutions:
                if self.branching_scheme.better(self.worst, solution):
                    self.worst = solution

        return True

    def display_init(self, verbose):
        if verbose:
            print("-"*79)
            print(
                    '{:16}'.format("Time")
                    + '{:40}'.format("Value")
                    + '{:32}'.format("Comment"))
            print("-"*79)

    def display(self, message, start, verbose):
        if verbose:
            value = self.branching_scheme.display(self.best)
            print(
                    '{:<16.3f}'.format(time.time() - start)
                    + '{:40}'.format(value)
                    + '{:32}'.format(message))

    def display_end(self, start, verbose):
        if verbose:
            current_time = time.time() - start
            value = self.branching_scheme.display(self.solutions[0])
            print("---")
            print(f"Time: {current_time}")
            print(f"Value: {value}")


def add_to_history_and_queue(branching_scheme, history, queue, node):
    # If node is not comparable, stop.
    if branching_scheme.comparable(node):
        bucket = branching_scheme.Bucket(node)
        if bucket not in history:
            history[bucket] = []
        list_of_nodes = history[bucket]

        # Check if node is dominated.
        for n in list_of_nodes:
            if branching_scheme.dominates(n, node):
                return False

        # Remove dominated nodes from history and queue.
        index = 0
        while index < len(list_of_nodes):
            n = list_of_nodes[index]
            if branching_scheme.dominates(node, n):
                queue.remove(n)
                list_of_nodes[index] = list_of_nodes[-1]
                list_of_nodes.pop()
            else:
                index += 1

        # Add node to history.
        list_of_nodes.append(node)

    # Add to queue.
    queue.add(node)

    return True


def remove_from_history(branching_scheme, history, node):
    if branching_scheme.comparable(node):
        bucket = branching_scheme.Bucket(node)
        list_of_nodes = history[bucket]
        index = 0
        while index < len(list_of_nodes):
            node_2 = list_of_nodes[index]
            if node_2 is node:
                list_of_nodes[index] = list_of_nodes[-1]
                list_of_nodes.pop()
                if not list_of_nodes:
                    del history[bucket]
                return
            else:
                index += 1


def remove_from_history_and_queue(branching_scheme, history, queue, pos):
    node = queue[pos]
    # Remove from history.
    remove_from_history(branching_scheme, history, node)
    # Remove from queue.
    queue.pop(pos)
