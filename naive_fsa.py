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

        self.MAX_MATCH_SEARCH = (options['max_match_search']
                if isinstance(options, dict) and 'max_match_search' in options
                else 100)

    def search(self, sequence, start=0):
        """
        Brute force to search the FSA in the sequence for the first occurence.
        """
        self.current = self.start
        is_success, start_pos, next_start_pos = self.match(sequence, start)

        while start_pos < len(sequence):
            if is_success:
                return (True, start_pos, next_start_pos)

            start_pos += 1
            is_success, start_pos, next_start_pos = self.match(sequence, start_pos)

        return (False, start, next_start_pos)

    def match(self, sequence, start=0):
        """
        Test whether a sequence is matched by the FSA

        :param sequence , a collection that can be randomly accessed using an index
        :param start , the start point to search

        :return a tuple of 3 value: (match_success, end_point)
            If match_success is True, the end_point will be the index right after the tail
            of the the matched pattern.
            Otherwise, the end_point will be -1.
        """
        self.current = self.start
        if start >= len(sequence):
            return (False, start, -1)

        pos = start
        count, previous = 0, None # used to check infinite loops

        while 0 <= pos and pos < len(sequence) and self.current != self.end:

            # When success, pos will increase by 1(default) or length of the matched symbol.
            # When failed, pos will be at the start point.
            (is_success, pos) = self._feed(sequence, pos)
            if is_success: continue
            else: break

            # check if the machine is getting stuck in a infinite loop
            count = count + 1 if previous == self.current else 0
            previous = self.current
            if count > self.MAX_MATCH_SEARCH:
                raise ValueError("Keeping stuck in current state: %s" % str(self.current))

        return ((self.current == self.end), start, pos)

    def _transfer_to(self, new_state):
        #print "transfer from", self.current, "to", new_state
        self.current = new_state

        # move along if any direct transition path exists
        detail = self.states[self.current]
        while 'direct' in detail:
            #print "  --> directly from", self.current, "to", detail['direct']
            self.current = detail['direct']
            detail = self.states[self.current]

    def _feed(self, sequence, start_pos, matchmode=True):
        """
        Find if the sequence matched any FSA machine
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
                        if match.start() == start_pos:
                            self._transfer_to(target)
                            return (True, match.end())
                        break

                elif start_pos == sequence.find(symbol, start_pos):
                    # common string
                    self._transfer_to(target)
                    return (True, start_pos + len(symbol))

                else:
                    pass

        if 'default' in detail:
            self._transfer_to(detail['default'])
            return (True, start_pos + 1)

        # In match mode, -1 terminates the matching and suggests that no pattern is found.
        # while in other modes, just move to the next position
        if matchmode:
            return (False, start_pos)
        else:
            return (True, start_pos + 1)

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

    html = "hello aefgef3ooo"
    print "length of", html, "is", len(html)
    print "match '%s' status:" % html, fsa.match(html, 0)
 
    html = "aefgef3"
    print "length of", html, "is", len(html)
    print "match '%s' status:" % html, fsa.match(html, 0)

    html = "hello aefgef3ooo"
    print "length of", html, "is", len(html)
    print "match '%s' status:" % html, fsa.search(html, 0)

