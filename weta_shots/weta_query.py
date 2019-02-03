import re
from collections import defaultdict

from weta_importer import WetaImporter
from weta_shot import Shot, ShotGroup


class WetaQuery():
    def __init__(self, data):
        self.data = data
        self.selected_data = None
        self.selection_method = None

    def filter_multiple(self, args):
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

        parsed_args = re.split(r'''(\w+\s*=\"[\w|\s|-]+\")|(\w+\s*=[\w|-]+)|(AND|and)|(OR|or)|([()]+)''', args)
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
                data_stack.append(set(self.filter_single(self.data, parsed_arg)))

        while len(ops_stack) > 0:
            data_stack.append(operate(ops_stack.pop(), data_stack.pop(), data_stack.pop()))

        self.data = list(data_stack.pop())

    def filter_single(self, data, arg_str):
        arg_str = arg_str.replace('"', '')
        parsed_args = re.search(r'''(\w+)='*([\w|\s|-]+)'*''', arg_str)
        data = list(filter(lambda d: getattr(d, parsed_args[1]) == parsed_args[2], data))
        return data

    def aggregate(self, aggregate_keys):
        groups = defaultdict(list)
        for d in self.data:
            group_index = tuple(getattr(d, k) for k in aggregate_keys)
            groups[group_index].append(d)

        aggregated_data = []
        for group in groups.values():
            shot_group = ShotGroup(shots=group, aggregrations=self.selection_method)
            aggregated_data.append(shot_group)

        self.data = aggregated_data

    def select(self):
        columns = self.selection_method.keys()
        rows = [[str(getattr(d, col)) for col in columns] for d in self.data]
        self.selected_data = [','.join(row) for row in rows]

    def sort(self, sorting_keys):
        self.data.sort(key=lambda s: tuple(getattr(s, k) for k in sorting_keys))

    def output(self):
        for d in self.selected_data:
            print(d)

    def set_selection_method(self, selections):
        selections_with_aggregation = dict()

        for sel in selections:
            parsed_sel = sel.split(':')
            selections_with_aggregation[parsed_sel[0]] = parsed_sel[1] if len(parsed_sel) > 1 else None

        self.selection_method = selections_with_aggregation


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
    querier = WetaQuery(data)

    if args.filter:
        querier.filter_multiple(args.filter)

    if args.order:
        sorting_keys = args.order.split(',')
        querier.sort(sorting_keys=sorting_keys)

    querier.set_selection_method(args.select.split(','))

    if args.group:
        aggregate_keys = args.group.split(',')
        querier.aggregate(aggregate_keys=aggregate_keys)

    querier.select()
    querier.output()


if __name__ == '__main__':
    main()
