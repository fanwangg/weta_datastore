import re
from collections import defaultdict

from weta_importer import WetaImporter
from weta_shot import Shot, ShotGroup


def filter_multiple(all_data, args):
    def operate(op, second, first):
        if op == 'AND':
            return first & second
        elif op == 'OR':
            return first | second
        else:
            print(f'Wrong op {op}')

    def precedence(current_op, op_from_ops):
        if op_from_ops == '(' or op_from_ops == ')':
            return False
        elif (current_op == 'OR') and (op_from_ops == 'AND'):
            return False
        else:
            return True

    parsed_args = re.split(r'''(\w+\s*=\"[\w\s]+\")|(\w+\s*=[\w]+)|(AND|and)|(OR|or)|([()]+)''', args)
    parsed_args = [pa for pa in parsed_args if pa and pa != ' ']
    data_stack, ops_stack = [], []

    for parsed_arg in parsed_args:
        if parsed_arg == '(':
            ops_stack.append('(')
        elif parsed_arg == ')':
            data_stack.append()
            while ops_stack[-1] != '(':
                data_stack.append(operate(ops_stack.pop(), data_stack.pop(), data_stack.pop()))
            ops_stack.pop()
        elif parsed_arg in ['AND', 'OR']:
            while len(ops_stack) != 0 and precedence(parsed_arg, ops_stack[-1]):
                data_stack.append(operate(ops_stack.pop(), data_stack.pop(), data_stack.pop()))
            ops_stack.append(parsed_arg)
        else:
            data_stack.append(set(filter_single(all_data, parsed_arg)))

    while len(ops_stack) > 0:
        data_stack.append(operate(ops_stack.pop(), data_stack.pop(), data_stack.pop()))

    return list(data_stack.pop())


def filter_single(data, arg_str):
    arg_str = arg_str.replace('"', '')
    parsed_args = re.search(r'''(\w+)='*([\w|\s|-]+)'*''', arg_str)
    data = list(filter(lambda d: getattr(d, parsed_args[1]) == parsed_args[2], data))
    return data


def aggregate_data(data, aggregate_keys, aggregate_methods):
    groups = defaultdict(list)
    for d in data:
        group_index = tuple(getattr(d, k) for k in aggregate_keys)
        groups[group_index].append(d)

    aggregated_data = []
    for group in groups.values():
        shot_group = ShotGroup(shots=group, aggregrations=aggregate_methods)
        aggregated_data.append(shot_group)

    return aggregated_data


def select_column(data, columns):
    rows = [[str(getattr(d, col)) for col in columns] for d in data]
    return [','.join(row) for row in rows]


def sort_by_order(data, sorting_keys):
    data.sort(key=lambda s: tuple(getattr(s, k) for k in sorting_keys))
    return data


def output(data):
    for d in data:
        print(d)


def parse_selection(selections):
    selections_with_aggregation = dict()

    for sel in selections:
        parsed_sel = sel.split(':')
        selections_with_aggregation[parsed_sel[0]] = parsed_sel[1] if len(parsed_sel) > 1 else None

    return selections_with_aggregation


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parameter for the queries')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-s', '--select', required=True)
    parser.add_argument('-o', '--order', nargs='?')
    parser.add_argument('-f', '--filter', nargs='?')
    parser.add_argument('-g', '--group', nargs='?')

    args = parser.parse_args()
    if args.debug:
        print(args)

    data = WetaImporter.pickle_load('../output.pkl')

    if args.filter:
        data = filter_multiple(data, args.filter)

    if args.order:
        sorting_keys = args.order.split(',')
        data = sort_by_order(data, sorting_keys=sorting_keys)

    selected_method = parse_selection(args.select.split(','))

    if args.group:
        aggregate_keys = args.group.split(',')
        data = aggregate_data(data,
                              aggregate_keys=aggregate_keys,
                              aggregate_methods=selected_method)

    selected_data = select_column(data, columns=selected_method.keys())

    output(selected_data)


if __name__ == '__main__':
    main()
