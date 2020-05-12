"""
Iteration 2

Usage:
  iteration_2.py --config_path=<config_path> --verbose=<verbose>

Options:
    --config_path=<config_path>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python iteration_2.py --config_path="../input/config_files/v2.json" --verbose=1
"""
import json
from docopt import docopt


# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

settings = json.load(open(arguments['--config_path']))

# code to run Iteration 2