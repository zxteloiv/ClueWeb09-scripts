#!/usr/bin/env python2
# coding: utf-8

import re

self.RETYPE = type(re.compile('kagamine'))

class FiniteStateAutomata(object):
    def __init__(self, states, start, end):
        """
        Create an FSA object using a list of states.
        Each state is a dict with given keys:

        :param states , a dict of state objects.
            Each key is a state name, corresponding item is another dict.
                Each item contains
                trans: a list of independent transitions
                    transition: (symbol, target_state_name)
                default_target: default
                direct_target: default

        :param start , the name of the start state
        :param end , the name of the end state
        """
        self.states = set()
        self.current = None

        fsa = FiniteStateAutomata()
        fsa.states = states

        fsa.current = start

    def check(self, contents):
        pass

    def run_over(self, iterable):
        detail = states[self.current]
        while 'direct' in detail:
            self.current = detail['direct']
            detail = states[self.current]

        if 'trans' in detail:
            for (symbol, target) in detail['trans']:
                if isinstance(symbol, RETYPE) and symbol.match(iterable):
                    self.current = target
                    return symbol.sub('', iterable)
                elif re.match('^' + symbol, iterable):
                    return re
                else:
                    pass
            else:
                if 'default' in detail:
                    self.current = detail['default']
                else:
                    pass

        pass

if __name__ == "__main__":
    states = {
            "start": {
                # a state without "default" stays there if no known symbol is encountered
                "trans": [('a', 'first'), ('b', 'second')],
                },
            "first": {
                # a state with re pattern symbol will use the pattern to match remaining
                "trans": [(re.compile('ef'), 'second')]
                },
            "second": {
                # a state with "defaul" goes there if no known symbol is encountered
                "default": "first",
                "trans": [('3', 'third')]
                },
            "third": {
                # a state with "direct" key goes directly to that state
                "direct": "end"
                }
            "end": {
                }
            }

    fsa = FiniteStateAutomata(states, start="start", end="end")

    html = "hello abcefef3"
            


