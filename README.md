# Tree search Solver (Python)

A solver based on heuristic tree search.

This is the Python3 version of the C++ package [fontanf/treesearchsolver](https://github.com/fontanf/treesearchsolver).

![treesearch](img/treesearch.jpg?raw=true "treesearch")

[image source](https://commons.wikimedia.org/wiki/File:Saint-L%C3%A9ger-l%C3%A8s-Domart,arbre_de_la_croix_Notre-Dame_14.jpg)

## Description

The goal of this repository is to provide a simple framework to quickly implement algorithms based on heuristic tree search.

Solving a problem only requires a couple hundred lines of code (see examples).

Algorithms:
* Greedy `greedy`
* Best First Search `best_first_search`
* Iterative Beam Search `iterative_beam_search`

## Examples

[Travelling salesman problem](examples/travellingsalesman.py)

## Usage, running examples from command line

Install
```shell
pip3 install treesearchsolverpy
```

Running an example:
```shell
mkdir -p data/travellingsalesman/instance
python3 -m examples.travellingsalesman -a generator -i data/travellingsalesman/instance
python3 -m examples.travellingsalesman -a iterative_beam_search -i data/travellingsalesman/instance_50.json
```

Update:
```shell
pip3 install --upgrade treesearchsolverpy
```

## Usage, Python library

See examples.

