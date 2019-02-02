from weta_importer import Shot, pickle_load


def select_column(data, columns):
    rows = [[getattr(d, col) for col in columns] for d in data]
    return [','.join(row) for row in rows]


def sort_by_order(data, sorting_keys):
    data.sort(key=lambda s: tuple(getattr(s, k) for k in sorting_keys))
    return data


def output(data):
    for d in data:
        print(d)


if __name__ == '__main__':
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

    data = pickle_load('output.pkl')

    if args.order:
        sorting_keys = args.order.split(',')
        data = sort_by_order(data, sorting_keys=sorting_keys)

    selected_column = args.select.split(',')
    selected_data = select_column(data, columns=selected_column)

    output(selected_data)
