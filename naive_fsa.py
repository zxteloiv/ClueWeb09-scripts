#!/usr/bin/env python2
# coding: utf-8

import re

RETYPE = type(re.compile('kagamine'))

class FiniteStateAutomata(object):
    def __init__(self, states, start, end, options={}):
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
        self.states = states
        self.current = start
        self.start = start
        self.end = end

        self.MAX_MATCH_SEARCH = (options['max_match_search']
                if isinstance(options, dict) and 'max_match_search' in options
                else 100)

    def match(self, sequence, start=0):
        """
        Test whether a sequence is matched by the fsa
        """
        if start >= len(sequence):
            return (False, start, -1)

        pos = start

        count = 0
        previous = None
        while pos < len(sequence) and self.current != self.end:

            pos = self.feed(sequence, pos)

            # check if the machine is getting stuck in a infinite loop
            count = count + 1 if previous == self.current else 0
            previous = self.current
            if count > self.MAX_MATCH_SEARCH:
                raise ValueError("Keeping stuck in current state: %s" % str(self.current))

        return ((True, start, pos) if self.current == self.end
                else (False, start, -1))

    def transfer_to(self, new_state):
        print "transfer from", self.current, "to", new_state
        self.current = new_state

        # move along if any direct transition path exists
        detail = self.states[self.current]
        while 'direct' in detail:
            print "  --> directly from", self.current, "to", detail['direct']
            self.current = detail['direct']
            detail = self.states[self.current]

    def feed(self, sequence, start_pos, matchmode=True):
        """
        """
        if self.current not in self.states:
            raise ValueError('State %s cannot be found' % self.current)

        detail = self.states[self.current]
        if 'trans' in detail:

            for (symbol, target) in detail['trans']:

                if isinstance(symbol, RETYPE):
                    # regular expression object symbol
                    for match in symbol.finditer(sequence, start_pos):
                        # consider only the first match
                        self.transfer_to(target)
                        return match.end()

                elif start_pos == sequence.find(symbol, start_pos):
                    # common string
                    self.transfer_to(target)
                    return start_pos + len(symbol)

                else:
                    pass

        if 'default' in detail:
            self.transfer_to(detail['default'])

        if matchmode:
            return -1

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
                },
            "end": {
                }
            }

    fsa = FiniteStateAutomata(states, start="start", end="end")

    html = "hello abcefef3"
    print "match '%s' status:" % html, fsa.match(html, 0)
            


