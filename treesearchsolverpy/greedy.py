from .commons import SolutionPool

import time
import random


def greedy(branching_scheme, **parameters):
    # Read parameters.
    start = time.time()
    seed = parameters.get(
            "seed", 0)
    maximum_pool_size = parameters.get(
            "maximum_pool_size", 1)
    time_limit = parameters.get(
            "time_limit", float('inf'))
    verbose = parameters.get(
            "verbose", True)

    if verbose:
        print("======================================")
        print("           TreeSearchSolver           ")
        print("======================================")
        print()
        print("Algorithm")
        print("---------")
        print("Greedy")
        print()
        print("Parameters")
        print("----------")
        print(f"Maximum pool size:          {maximum_pool_size}")
        print(f"Seed:                       {seed}")
        print(f"Time limit:                 {time_limit}")

    random.seed(seed)

    solution_pool = SolutionPool(branching_scheme, maximum_pool_size)
    number_of_nodes = 0

    current_node = branching_scheme.root()

    while True:

        # Check time limit.
        current_time = time.time()
        if current_time - start > time_limit:
            break

        number_of_nodes += 1

        # Generate children.
        best_child = None
        while not branching_scheme.infertile(current_node):
            if best_child is not None \
                    and best_child < current_node:
                break
            child = branching_scheme.next_child(current_node)
            if child is None:
                continue
            # Update best solution.
            if branching_scheme.better(child, solution_pool.worst):
                solution_pool.add(child)
            if branching_scheme.leaf(child):
                continue
            if best_child is None or best_child > child:
                best_child = child

        # Stop criteria.
        if best_child is None:
            break
        # Update current_node.
        current_node = best_child

    # Final display.
    solution_pool.display_end(start, verbose)
    if verbose:
        print(f"Number of nodes:             {number_of_nodes}")

    end = time.time()

    return {"solution_pool": solution_pool,
            "number_of_nodes": number_of_nodes,
            "elapsed_time": end - start}
