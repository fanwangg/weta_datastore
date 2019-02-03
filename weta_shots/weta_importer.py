import csv
import pickle

from weta_shot import Shot


class WetaImporter:
    def import_from_file(self, filename):
        shots = dict()
        with open(filename, newline='') as import_file:
            dict_reader = csv.DictReader(import_file, delimiter='|')
            for row in dict_reader:
                s = Shot.from_csv_row(row)
                shots[s.uid] = s

        return shots

    def import_file_and_store(self, filename, output_filename='output.pkl'):
        shots = self.import_from_file(filename)
        self.pickle_dump(shots, output_filename)

    def pickle_dump(self, data, filename):
        with open(filename, 'wb') as handle:
            pickle.dump(data, handle)

    @staticmethod
    def pickle_load(filename='output.pkl'):
        with open(filename, 'rb') as handle:
            data = pickle.load(handle)

        return list(data.values())


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parameter for the importer')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--filename', required=True, help='path for file to import')
    parser.add_argument('-o', '--output', help='path for output file')
    args = parser.parse_args()

    weta_importer = WetaImporter()
    if args.output:
        weta_importer.import_file_and_store(args.filename, args.output)
    else:
        weta_importer.import_file_and_store(args.filename)


if __name__ == '__main__':
    main()
