
class _SortedDict:

    def __init__(self):
        self._list = []

    def items(self):
        yield from self._list

    def keys(self):
        for key, _ in self._list:
            yield key

    def key_at(self, index):
        return self._list[index][0]

    def values(self):
        for _, value in self._list:
            yield value

    def value_at(self, index):
        return self._list[index][1]

    def _index_in_range(self, start, key, end):
        if start == end:
            return start
        midpoint = start + ((end - start) // 2)
        if self.key_at(midpoint) < key:
            return self._index_in_range(midpoint + 1, key, end)
        else:
            return self._index_in_range(start, key, midpoint)
    
    def _index(self, key):
        return self._index_in_range(0, key, len(self._list))

    def _has_key_at(self, key, index):
        if index == len(self._list):
            return False
        else:
            return self.key_at(index) == key

    def __getitem__(self, key):
        index = self._index(key)
        if self._has_key_at(key, index):
            return self.value_at(index)
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        index = self._index(key)
        if self._has_key_at(key, index):
            self._list[index] = (key, value)
        else:
            self._list.insert(index, (key, value))

    def __delitem__(self, key):
        index = self._index(key)
        if self._has_key_at(key, index):
            del self._list[index]
        else:
            raise KeyError(key)

    def __contains__(self, key):
        return self._has_key_at(key, self._index(key))

def _check_type(obj, typ):
    if type(obj) is not typ:
        raise TypeError(type(obj))

def _check_minimum(num, minimum):
    if num < minimum:
        raise ValueError(num)

def _strictly_round(unrounded):
    rounded = int(unrounded)
    if rounded != unrounded:
        raise ValueError(unrounded)
    return rounded

def _split_int(num, ways):
    q = num // ways
    r = num % ways
    for _ in range(r):
        yield q + 1
    for _ in range(r, ways):
        yield q

class _ErrInsufficient(ValueError):
    pass

class _RowNum:

    def __init__(self, num):
        _check_type(num, int)
        _check_minimum(num, 1)
        self._num = num

    def index(self):
        return self._num - 1

    def __str__(self):
        return f'{self._num}.'

    def from_index(index):
        return _RowNum(index + 1)

class _Units:

    def __init__(self, units):
        _check_type(units, int)
        _check_minimum(units, 0)
        self._units = units

    def __add__(self, other):
        check_type(other, _Units)
        return _Units(self._units + other._units)

    def __sub__(self, other):
        _check_type(other, _Units)
        if self._units < other._units:
            raise _ErrInsufficient(self)
        return _Units(self._units - other._units)

    def __int__(self):
        return self._units

    def __str__(self):
        return f'{self._units}x'

class _Cents:

    def __init__(self, cents):
        _check_type(cents, int)
        self._cents = cents

    def check_positive(self):
        if self._cents < 0:
            raise ValueError(self)

    def __add__(self, other):
        _check_type(other, _Cents)
        return _Cents(self._cents + other._cents)

    def __sub__(self, other):
        _check_type(other, _Cents)
        return _Cents(self._cents - other._cents)

    def __int__(self):
        return self._cents

    def __str__(self):
        dollars = self._cents / 100
        if dollars < 0:
            return f'-${-dollars:.2f}'
        else:
            return f'${dollars:.2f}'

    def split(self, ways):
        for part in _split_int(self._cents, ways):
            yield _Cents(part)

    def from_dollars(dollars):
        return _Cents(_strictly_round(dollars * 100))

class _Balance:

    def __init__(self, cents):
        _check_type(cents, int)
        _check_minimum(cents, 0)
        self._cents = cents

    def check(self, cents):
        _check_type(cents, _Cents)
        cents.check_positive()
        if self._cents < cents._cents:
            raise _ErrInsufficient(self)

    def as_cents(self):
        return _Cents(self._cents)

    def __add__(self, cents):
        _check_type(cents, _Cents)
        cents.check_positive()
        return _Balance(self._cents + int(cents))

    def __sub__(self, cents):
        self.check(cents)
        return _Balance(self._cents - int(cents))

    def __int__(self):
        return self._cents

    def __str__(self):
        dollars = self._cents / 100
        return f'${dollars:.2f}'

    def split(self, ways):
        for part in _split_int(self._cents, ways):
            yield _Balance(part)

class _Minutes:

    def __init__(self, minutes):
        _check_type(minutes, int)
        _check_minimum(minutes, 0)
        self._minutes = minutes

    def __add__(self, other):
        check_type(other, _Minutes)
        return _Minutes(self._minutes + other._minutes)

    def __int__(self):
        return self._minutes

    def __str__(self):
        hours = self._minutes // 60
        minutes = self._minutes % 60
        return f'{hours}h {minutes:02}m'

    def split(self, ways):
        for part in _split_int(self._minutes, ways):
            yield _Minutes(part)

    def as_hours(self):
        return self._minutes / 60

    def from_hours(hours):
        return _Minutes(strictly_round(hours * 60))

class _Wage:

    def __init__(self, cents, minutes):
        _check_type(cents, _Cents)
        _check_type(minutes, _Minutes)
        cents = int(cents)
        hours = minutes.as_hours()
        if hours == 0:
            self._hourly = None
        else:
            self._hourly = _Cents(int(cents / hours))

    def __str__(self):
        if self._hourly is None:
            return 'N/A'
        else:
            return f'{self._hourly}/h'

class _Inventory:

    def __init__(self):
        self._dict = _SortedDict()

    def items(self):
        yield from self._dict.items()

    def label_at(self, index):
        return self._dict.key_at(index)

    def acquire(self, label, units):
        _check_type(label, str)
        _check_type(units, _Units)
        if int(units) == 0:
            return
        elif label in self._dict:
            self._dict[label] += units
        else:
            self._dict[label] = units

    def discard(self, label, units):
        _check_type(label, str)
        _check_type(units, _Units)
        if int(units) == 0:
            return
        elif label not in self._dict:
            raise _ErrInsufficient(_Units(0))
        elif int(self._dict[label]) == int(units):
            del self._dict[label]
        else:
            self._dict[label] -= units

    def relabel(self, old_label, new_label, units):
        _check_type(new_label, str)
        self.discard(old_label, units)
        self.acquire(new_label, units)

    def split(self, ways):
        inventories = [_Inventory() for _ in range(ways)]
        index = 0
        for label, units in self._dict.items():
            for part in _split_int(int(units), ways):
                index %= ways
                inventories[index].aquire(label, _Units(part))
                index += 1
            index += int(units)
        return inventories

    def merge(self, other):
        _check_type(other, _Inventory)
        for label, units in other._dict.items():
            self.acquire(label, units)

class _Branch:

    def __init__(self, name, description):
        _check_type(name, str)
        _check_type(description, str)
        self._name = name
        self._description = description
        self._balance = _Balance(0)
        self._profit = _Cents(0)
        self._time_spent = _Minutes(0)
        self._inventory = _Inventory()

    def name(self):
        return self._name

    def description(self):
        return self._description

    def rename(self, name):
        _check_type(name, str)
        self._name = name

    def describe(self, description):
        _check_type(description, str)
        self._description = description

    def balance(self):
        return self._balance

    def profit(self):
        return self._profit

    def time_spent(self):
        return self._time_spent

    def wage(self):
        return _Wage(self._profit, self._time_spent)

    def deposit(self, cents):
        self._balance += cents

    def withdraw(self, cents):
        self._balance -= cents

    def earn(self, cents):
        self._balance += cents
        self._profit += cents

    def spend(self, cents):
        self._balance -= cents
        self._profit -= cents

    def clock(self, minutes_spent):
        self._time_spent += minutes_spent

    def inventory(self):
        return self._inventory

    def _split_name(self, ways):
        for i in range(ways):
            yield f'{self._name} ({i+1})'

    def split(self, ways):
        _check_minimum(ways, 2)
        names       = self._split_name(ways)
        balances    = self._balance.split(ways)
        profits     = self._profit.split(ways)
        times_spent = self._time_spent.split(ways)
        inventories = self._inventory.split(ways)
        zipper = zip(names, balances, profits, times_spent, inventories)
        for name, balance, profit, time_spent, inventory in zipper:
            child = _Branch(name, self._description)
            child._balance      = balance
            child._profit       = profit
            child._time_spent   = time_spent
            child._inventory    = inventory
            yield child

    def merge(self, other):
        _check_type(other, _Branch)
        self._balance       += other._balance.as_cents()
        self._profit        += other._profit
        self._time_spent    += other._time_spent
        self._inventory.merge(other._inventory)

_branches = _SortedDict()
_branches['Initial'] = _Branch('Initial', 'no description')

def _branch_total(get):
    return sum(int(get(branch)) for branch in _branches.values())

def _total_balance():
    return _Balance(_branch_total(_Branch.balance))

def _total_profit():
    return _Cents(_branch_total(_Branch.profit))

def _total_time_spent():
    return _Minutes(_branch_total(_Branch.time_spent))

def _total_wage():
    return _Wage(_total_profit(), _total_time_spent())

def _check_balance(cents):
    _total_balance().check(cents)

def _cumulative_balance_distribution():
    total = int(_total_balance())
    so_far = 0
    for branch in _branches.values():
        so_far += int(branch.balance())
        cumulative_ratio = so_far / total
        yield branch, cumulative_ratio

def _int_distribution_by_balance(total):
    _check_minimum(total, 0)
    distributed = 0
    for branch, cumulative_ratio in _cumulative_balance_distribution():
        target = int(total * cumulative_ratio)
        distribution = target - distributed
        yield branch, distribution
        distributed = target

def _distribute_by_balance(total, into):
    typ = type(total)
    for branch, distribution_int in _int_distribution_by_balance(int(total)):
        distribution = typ(distribution_int)
        into(branch, distribution)

def _convert_table_data(data):
    return [[str(cell) for cell in row] for row in data]

def _num_columns(data):
    return max(len(row) for row in data)

def _column_widths(data):
    widths = [0] * _num_columns(data)
    for row in data:
        for column, cell in enumerate(row):
            widths[column] = max(widths[column], len(cell))
    return widths

def _convert_alignment(alignment):
    if alignment == 'l':
        return '<'
    elif alignment == 'r':
        return '>'
    else:
        raise ValueError(alignment)

def _convert_alignments(alignments):
    return [_convert_alignment(alignment) for alignment in alignments]

def _convert_paddings(paddings):
    return [' ' * int(padding) for padding in paddings]

def _table(data, alignments, paddings):
    data = _convert_table_data(data)
    column_widths = _column_widths(data)
    num_columns = len(column_widths)
    if len(alignments) != num_columns:
        raise ValueError(alignments)
    if len(paddings) != num_columns:
        raise ValueError(paddings)
    alignments  = _convert_alignments(alignments)
    paddings    = _convert_paddings(paddings)
    rows = (
        ''.join(
            f'{paddings[column]}{cell:{alignments[column]}{column_widths[column]}}'
            for column, cell in enumerate(row))
        for row in data)
    return '\n'.join(rows)

_history = []

class _ItemInterface:

    def __init__(self, branch, label):
        _check_type(branch, _Branch)
        _check_type(label, str)
        self._branch = branch
        self._label = label
        self._units = _Units(1)

    def __str__(self):
        string = f'branch(\'{self._branch.name()}\').item(\'{self._label}\')'
        if int(self._units) == 1:
            return string
        else:
            return f'{string}.units({int(self._units)})'

    def _inventory(self):
        return self._branch.inventory()

    def units(self, units):
        self._units = _Units(units)
        return self

    def relabel(self, label):
        self._inventory().relabel(self._label, label, self._units)
        self._label = label
        _history.append(f'{self}.relabel(\'{label}\')')

    def acquire(self):
        self._inventory().acquire(self._label, self._units)
        _history.append(f'{self}.acquire()')

    def discard(self):
        self._inventory().discard(self._label, self._units)
        _history.append(f'{self}.discard()')

    def buy(self, dollars_spent):
        cents_spent = _Cents.from_dollars(dollars_spent)
        self._branch.spend(cents_spent)
        self.acquire()
        _history.append(f'{self}.buy({dollars_spent})')

    def sell(self, dollars_earned):
        cents_earned = _Cents.from_dollars(dollars_earned)
        cents_earned.check_positive()
        self.discard()
        self._branch.earn(cents_earned)
        _history.append(f'{self}.sell({dollars_earned})')

class _BranchInterface:

    def __init__(self, branch):
        _check_type(branch, _Branch)
        self._branch = branch

    def __str__(self):
        return f'branch(\'{self._branch.name()}\')'

    def name(self):
        print(self._branch.name())
        
    def description(self):
        print(self._branch.description())

    def rename(self, name):
        _check_type(name, str)
        if name in _branches:
            raise ValueError(name)
        _history.append(f'{self}.rename(\'{name}\')')
        del _branches[self._branch.name()]
        self._branch.rename(name)
        _branches[self._branch.name()] = self._branch

    def describe(self, description):
        self._branch.describe(description)
        _history.append(f'{self}.describe(\'{description}\')')

    def summary(self):
        data = [['Balance', 'Profit', 'Time Spent', 'Wage'],
                [self._branch.balance(),
                 self._branch.profit(),
                 self._branch.time_spent(),
                 self._branch.wage()]]
        print(_table(data, 'rrrr', '0333'))

    def deposit(self, dollars):
        cents = _Cents.from_dollars(dollars)
        self._branch.deposit(cents)
        _history.append(f'{self}.deposit({dollars})')

    def withdraw(self, dollars):
        cents = _Cents.from_dollars(dollars)
        self._branch.withdraw(cents)
        _history.append(f'{self}.withdraw({dollars})')

    def earn(self, dollars):
        cents = _Cents.from_dollars(dollars)
        self._branch.earn(cents)
        _history.append(f'{self}.earn({dollars})')

    def spend(self, dollars):
        cents = _Cents.from_dollars(dollars)
        self._branch.spend(cents)
        _history.append(f'{self}.spend({dollars})')

    def clock(self, hours_spent):
        minutes_spent = _Minutes.from_hours(hours_spent)
        self._branch.clock(minutes_spent)
        _history.append(f'{self}.clock({hours_spent})')

    def inventory(self):
        data = [['', '', 'Units']]
        data.extend([_RowNum.from_index(index), label, units]
                    for index, (label, units)
                    in enumerate(self._branch.inventory().items()))
        print(_table(data, 'llr', '013'))

    def item(self, num_or_label):
        label = None
        if type(num_or_label) is str:
            label = num_or_label
        else:
            index = _RowNum(num_or_label).index()
            label = self._branch.inventory().label_at(index)
        return _ItemInterface(self._branch, label)

    def split(self, ways):
        children = list(self._branch.split(ways))
        for child in children:
            if child.name() in _branches:
                raise ValueError(child.name())
        for child in children:
            _branches[child.name()] = child
        del _branches[self._branch.name()]
        _history.append(f'{self}.split({ways})')

    def merge(self, other):
        _check_type(other, _BranchInterface)
        self._branch.merge(other._branch)
        del _branches[other._branch.name()]
        _history.append(f'{self}.merge({other})')

def branch(num_or_name):
    branch = None
    if type(num_or_name) is str:
        branch = _branches[num_or_name]
    else:
        index = _RowNum(num_or_name).index()
        branch = _branches.value_at(index)
    return _BranchInterface(branch)

def branch_names():
    data = [[_RowNum.from_index(index), name]
            for index, name in enumerate(_branches.keys())]
    print(_table(data, 'll', '01'))

def branch_descriptions():
    for index, branch in enumerate(_branches.values()):
        print(_RowNum.from_index(index), branch.name())
        print()
        print(branch.description())
        print()

def branch_summaries():
    data = [['', '', 'Balance', 'Profit', 'Time Spent', 'Wage']]
    data.extend([_RowNum.from_index(index),
                 branch.name(),
                 branch.balance(),
                 branch.profit(),
                 branch.time_spent(),
                 branch.wage()]
                for index, branch in enumerate(_branches.values()))
    print(_table(data, 'llrrrr', '013333'))

def summary():
    data = [['Balance', 'Profit', 'Time Spent', 'Wage'],
            [_total_balance(),
             _total_profit(),
             _total_time_spent(),
             _total_wage()]]
    print(_table(data, 'rrrr', '0333'))

def deposit(dollars):
    cents = _Cents.from_dollars(dollars)
    _distribute_by_balance(cents, _Branch.deposit)
    _history.append(f'deposit({dollars})')

def withdraw(dollars):
    cents = _Cents.from_dollars(dollars)
    _check_balance(cents)
    _distribute_by_balance(cents, _Branch.withdraw)
    _history.append(f'withdraw({dollars})')

def earn(dollars):
    cents = _Cents.from_dollars(dollars)
    _distribute_by_balance(cents, _Branch.earn)
    _history.append(f'earn({dollars})')

def spend(dollars):
    cents = _Cents.from_dollars(dollars)
    _check_balance(cents)
    _distribute_by_balance(cents, _Branch.spend)
    _history.append(f'spend({dollars})')

def clock(hours_spent):
    minutes_spent = _Minutes.from_hours(hours_spent)
    _distribute_by_balance(minutes_spent, _Branch.clock)
    _history.append(f'clock({hours_spent})')

def history():
    print('\n'.join(_history))

import pickle

def _check_branches(branches):
    _check_type(branches, _SortedDict)
    for name, branch in branches.items():
        _check_type(name, str)
        _check_type(branch, _Branch)
        if branch.name() != name:
            raise ValueError(name)

def _check_history(history):
    _check_type(history, list)
    for entry in history:
        _check_type(entry, str)

def _set_state(state):
    global _branches
    global _history
    branches, history = state
    _check_branches(branches)
    _check_history(history)
    _branches = branches
    _history = history

def _get_state():
    return _branches, _history

def save(file_name):
    file = open(file_name, 'wb')
    contents = _get_state()
    pickle.dump(contents, file)

def load(file_name):
    file = open(file_name, 'rb')
    contents = pickle.load(file)
    _set_state(contents)

def reset():
    global _branches
    global _history
    _branches = _SortedDict()
    _branches['Initial'] = _Branch('Initial', 'no description')
    _history = []
