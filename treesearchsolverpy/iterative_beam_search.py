import treesearchsolverpy.commons as ts

import math
import time
from sortedcontainers import SortedList


def iterative_beam_search(branching_scheme, **parameters):
    # Read parameters.
    start = time.time()
    maximum_pool_size = parameters.get(
            "maximum_pool_size", 1)
    minimum_size_of_the_queue = parameters.get(
            "minimum_size_of_the_queue", 1)
    maximum_size_of_the_queue = parameters.get(
            "maximum_size_of_the_queue", float('inf'))
    maximum_number_of_nodes = parameters.get(
            "maximum_number_of_nodes", float('inf'))
    growth_factor = parameters.get(
            "growth_factor", 2)
    time_limit = parameters.get(
            "time_limit", float('inf'))
    verbose = parameters.get(
            "verbose", True)

    if verbose:
        print("======================================")
        print("          Tree Search Solver          ")
        print("======================================")
        print()
        print("Algorithm")
        print("---------")
        print("Iterative Beam Search")
        print()
        print("Parameters")
        print("----------")
        print(f"Minimum size of the queue:  {minimum_size_of_the_queue}")
        print(f"Maximum size of the queue:  {maximum_size_of_the_queue}")
        print(f"Maximum number of nodes:    {maximum_number_of_nodes}")
        print(f"Growth factor:              {growth_factor}")
        print(f"Maximum pool size:          {maximum_pool_size}")
        print(f"Time limit:                 {time_limit}")

    # Setup structures.
    solution_pool = ts.SolutionPool(branching_scheme, maximum_pool_size)
    q = SortedList()
    q_next = SortedList()
    history = {}
    queue_size = minimum_size_of_the_queue
    number_of_nodes = 0
    # Initial display.
    solution_pool.display_init(verbose)
    while queue_size <= maximum_size_of_the_queue:
        # Display.
        message = f"q {queue_size}"
        solution_pool.display(message, start, verbose)
        # Reset structures.
        # Becomes False as soon as non-dominated nodes are pruned.
        stop = True
        # Becomes True if a time or node limit is reached.
        end = False
        q.clear()

        # Initialize queue with root node.
        q.add(branching_scheme.root())

        depth = 1
        while q:
            history.clear()
            q_next.clear()

            current_node = None
            while current_node is not None or q:
                # Check time limit.
                current_time = time.time()
                if current_time - start > time_limit:
                    end = True
                    break

                # Check node limit.
                if number_of_nodes > maximum_number_of_nodes:
                    end = True
                    break

                number_of_nodes += 1

                # Get the next processed node from the queue.
                if current_node is None:
                    current_node = q.pop(0)
                    # Check bound.
                    if branching_scheme.bound(
                            current_node, solution_pool.worst):
                        current_node = None
                        continue

                # Update stop.
                if len(q_next) == queue_size \
                        and q_next[-1] < current_node:
                    stop = False
                    break

                # Get next child.
                child = branching_scheme.next_child(current_node)
                if child is not None:
                    # Update best solution.
                    if branching_scheme.better(child, solution_pool.worst):
                        solution_pool.add(child)
                    # Add child to the queue.
                    if (
                            not branching_scheme.leaf(child)
                            and not branching_scheme.bound(
                                child, solution_pool.worst)):
                        # Update stop.
                        if len(q_next) >= queue_size:
                            stop = False
                        # Check if it is worth adding the child to the next
                        # queue.
                        if len(q_next) < queue_size or child < q_next[-1]:
                            # Add child to the queue (and the history).
                            ts.add_to_history_and_queue(
                                    branching_scheme, history, q_next, child)
                            # If the beam is too large, remove the less
                            # interesting nodes.
                            if len(q_next) > queue_size:
                                ts.remove_from_history_and_queue(
                                        branching_scheme,
                                        history,
                                        q_next,
                                        -1)

                # If current_node still has children, put it back to the queue.
                if branching_scheme.infertile(current_node):
                    current_node = None
                elif len(q) > 0 and q[0] < current_node:
                    q.add(current_node)
                    current_node = None

            q, q_next = q_next, q
            depth += 1

        if stop:
            break

        queue_size = math.ceil(growth_factor * queue_size)

    # Final display.
    solution_pool.display_end(start, verbose)
    if verbose:
        print(f"Number of nodes:             {number_of_nodes}")
        print(f"Maximum size of the queue:   {queue_size}")

    end = time.time()

    return {"solution_pool": solution_pool,
            "maximum_size_of_the_queue": queue_size,
            "number_of_nodes": number_of_nodes,
            "elapsed_time": end - start}
