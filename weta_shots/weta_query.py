import re
from collections import defaultdict

from weta_importer import Shot, ShotGroup, pickle_load


def preprocess_filter(filtering):
    parsed_results = re.search(r"(\w+)='*([\w|\s|-]+)'*", filtering)
    filter_results = {parsed_results[1]: parsed_results[2]}

    return filter_results


def filter_data(data, filter_keys):
    for k, v in filter_keys.items():
        data = list(filter(lambda d: getattr(d, k) == v, data))

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

    data = pickle_load('../output.pkl')

    if args.filter:
        filter_keys = preprocess_filter(args.filter)
        data = filter_data(data, filter_keys)

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
