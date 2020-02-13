import os
from ogle.parser.grammar_spec import terminals


class State(object):
    def __init__(self, name):
        self.name = name
        self.is_terminal = False
        if name in terminals:
            self.is_terminal = True
            self.token_value = terminals[name]
        self.first_set = set()
        self.follow_set = set()
        # Flag to compute first and follow sets
        self.visited = False
        self.rhs = []

    def __str__(self):
        return 'State({0} -> {1})'.format(self.name, self.rhs)

    def __repr__(self):
        return str(self)


class Grammar(object):
    def __init__(self):
        self.states = {}
        self.start_state = 'START'
        # Add all terminals to states
        for terminal in terminals:
            self.states[terminal] = State(terminal)
        # Read all rules and store in states
        self._read_grammar_file()
        self._calculate_first_sets()
        self._calculate_follow_sets()

    def _read_grammar_file(self):
        script_path = os.path.dirname(os.path.realpath(__file__))
        grammar_path = os.path.join(script_path, '..', '..', 'data', 'grammar', 'LL1Grammar.grm')
        with open(grammar_path, 'r') as file:
            for line in file:
                # Check if line is empty
                if '->' not in line:
                    continue
                # Split the grammar rule into lhs and rhs
                rule = line.split('->')
                lhs = rule[0].strip()
                rhs = rule[1].split()[:-1]
                # If rhs is lambda, put '#' instead
                if len(rhs) == 0:
                    rhs = '#'
                # Add rule to the states dict
                if lhs not in self.states:
                    self.states[lhs] = State(lhs)
                self.states[lhs].rhs.append(rhs)

    def _calculate_first_sets(self):
        for _, state in self.states.items():
            state.visited = False
        for _, state in self.states.items():
            if not state.visited:
                self._internal_first_set(state)

    def _internal_first_set(self, state):
        state.visited = True
        # If state X is terminal, First(X) = {X}
        if state.is_terminal:
            state.first_set.add(state.name)
            return

        # If state X has epsilon rhs, '#' ∈ First(X)
        if '#' in state.rhs:
            state.first_set.add('#')
        # Go through all productions of this state
        for rule in state.rhs:
            if rule == '#':
                continue
            nullable = True
            for symbol in rule:
                symbol_state = self.states[symbol]
                if not symbol_state.visited:
                    self._internal_first_set(symbol_state)
                state.first_set |= symbol_state.first_set - set('#')
                if '#' not in symbol_state.first_set:
                    nullable = False
                    break
            # If all states in the production are nullable
            if nullable:
                state.first_set.add('#')

    def _calculate_follow_sets(self):
        for _, state in self.states.items():
            state.visited = False
        for _, state in self.states.items():
            if not state.visited:
                self._internal_follow_set(state)

    def _internal_follow_set(self, state):
        state.visited = True
        # if state X is the start state, then its follow set is {$}
        if state.name == self.start_state:
            state.follow_set.add('$')
            return

        for occurrence_state_name, rule in self._all_occurrences(state.name):
            index = rule.index(state.name)
            nullable = True
            for i in range(index+1, len(rule)):
                state.follow_set |= self.states[rule[i]].first_set - set('#')
                if '#' not in self.states[rule[i]].first_set:
                    nullable = False
                    break
            if nullable:
                occurrence_state = self.states[occurrence_state_name]
                if not occurrence_state.visited:
                    self._internal_follow_set(occurrence_state)
                state.follow_set |= occurrence_state.follow_set

    # Returns all the rules that have the given 'name' inside
    # in the format of (lhs, rule)
    def _all_occurrences(self, name):
        occurrences = []
        for _, state in self.states.items():
            for rule in state.rhs:
                if name in rule:
                    occurrences.append((state.name, rule))
        return occurrences


if __name__ == '__main__':
    x = Grammar()
    for state_name, state_obj in x.states.items():
        print('{0} => {1}'.format(state_name, state_obj.follow_set))
    # print(x.states['PROGRAM'].first_set)
