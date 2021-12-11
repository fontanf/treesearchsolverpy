from .commons import SolutionPool, \
                     add_to_history_and_queue, \
                     remove_from_history_and_queue

import time
from sortedcontainers import SortedList


def best_first_search(branching_scheme, **parameters):
    # Read parameters.
    start = time.time()
    maximum_pool_size = parameters.get(
            "maximum_pool_size", 1)
    maximum_number_of_nodes = parameters.get(
            "maximum_number_of_nodes", float('inf'))
    time_limit = parameters.get(
            "time_limit", float('inf'))
    new_solution_callback = parameters.get(
            "new_solution_callback", None)
    verbose = parameters.get(
            "verbose", True)

    if verbose:
        print("======================================")
        print("          Tree Search Solver          ")
        print("======================================")
        print()
        print("Algorithm")
        print("---------")
        print("Best First Search")
        print()
        print("Parameters")
        print("----------")
        print(f"Maximum number of nodes:    {maximum_number_of_nodes}")
        print(f"Maximum pool size:          {maximum_pool_size}")
        print(f"Time limit:                 {time_limit}")

    # Setup structures.
    solution_pool = SolutionPool(branching_scheme, maximum_pool_size)
    queue = SortedList()
    history = {}
    number_of_nodes = 0
    maximum_size_of_the_queue = 1
    # Initial display.
    solution_pool.display_init(verbose)

    # Initialize queue with root node.
    root = branching_scheme.root()
    add_to_history_and_queue(branching_scheme, history, queue, root)
    current_node = None

    while current_node is not None or queue:

        # Check time limit.
        current_time = time.time()
        if current_time - start > time_limit:
            break

        # Check node limit.
        if number_of_nodes > maximum_number_of_nodes:
            break

        # Update statistics.
        number_of_nodes += 1
        maximum_size_of_the_queue = max(maximum_size_of_the_queue, len(queue))

        # Get the next processed node from the queue.
        if current_node is None:
            current_node = queue[0]
            remove_from_history_and_queue(
                    branching_scheme, history, queue, 0)
            # Check bound.
            if branching_scheme.bound(
                    current_node, solution_pool.worst):
                current_node = None
                continue

        # Get next child.
        child = branching_scheme.next_child(current_node)
        if child is not None:
            # Update best solution.
            if branching_scheme.better(child, solution_pool.worst):
                display = branching_scheme.better(child, solution_pool.best)
                solution_pool.add(child)
                # Display.
                if display:
                    message = f"node {number_of_nodes}"
                    solution_pool.display(message, start, verbose)
                    if new_solution_callback is not None:
                        new_solution_callback({
                            "solution_pool": solution_pool,
                            "number_of_nodes": number_of_nodes
                            })
            # Add child to the queue.
            if (
                    not branching_scheme.leaf(child)
                    and not branching_scheme.bound(
                        child, solution_pool.worst)):
                # Add child to the queue (and the history).
                add_to_history_and_queue(
                        branching_scheme, history, queue, child)

        # If current_node still has children, put it back to the queue.
        if branching_scheme.infertile(current_node):
            current_node = None
        elif len(queue) > 0 and queue[0] < current_node:
            add_to_history_and_queue(
                    branching_scheme, history, queue, current_node)
            current_node = None

    # Final display.
    solution_pool.display_end(start, verbose)
    if verbose:
        print(f"Number of nodes:             {number_of_nodes}")

    end = time.time()

    return {"solution_pool": solution_pool,
            "maximum_size_of_the_queue": maximum_size_of_the_queue,
            "number_of_nodes": number_of_nodes,
            "elapsed_time": end - start}
