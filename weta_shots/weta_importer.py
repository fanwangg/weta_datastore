import csv
import pickle

from enum import Enum
from typing import NamedTuple


class Shot(NamedTuple):
    project: str
    shot: str
    version: int
    status: str
    finish_date: str
    internal_bid: float
    created_date: str

    @property
    def uid(self):
        return (self.PROJECT, self.SHOT, self.VERSION)

    @property
    def PROJECT(self):
        return self.project

    @property
    def SHOT(self):
        return self.shot

    @property
    def VERSION(self):
        return self.version

    @property
    def STATUS(self):
        return self.status

    @property
    def FINISH_DATE(self):
        return self.finish_date

    @property
    def INTERNAL_BID(self):
        return self.internal_bid

    @property
    def CREATED_DATE(self):
        return self.created_date


class Aggregation(Enum):
    MIN = ('min', lambda s: min(s))
    MAX = ('max', lambda s: max(s))
    SUM = ('sum', lambda s: sum(s))
    COUNT = ('count', lambda s: len(s))
    COLLECT = ('collect', lambda s: s)

    def __call__(self, *args, **kwargs):
        return self.value[1](*args, **kwargs)

    @classmethod
    def from_string(cls, s):
        for c in cls:
            if c.value[0] == s:
                return c
        raise ValueError(cls.__name__ + ' has no value matching "{s}"')


class ShotGroup:
    def __init__(self, aggregrations: dict):
        self.shots = list()
        self.aggregating_method = dict()

        for k, v in aggregrations.items():
            self.aggregating_method[k] = Aggregation.from_string(v)

    def add_shots(self, shots):
        self.shots.extend(shots)

    def get_properity(self, property):
        return [getattr(s, property) for s in self.shots]

    def get_aggregated_property(self, property):
        aggregating_method = self.aggregating_method.get(property, Aggregation.COLLECT)
        return aggregating_method(self.get_properity(property))

    @property
    def PROJECT(self):
        return self.get_aggregated_property('PROJECT')

    @property
    def SHOT(self):
        return self.get_aggregated_property('SHOT')

    @property
    def VERSION(self):
        return self.get_aggregated_property('VERSION')

    @property
    def STATUS(self):
        return self.get_aggregated_property('STATUS')

    @property
    def FINISH_DATE(self):
        return self.get_aggregated_property('FINISH_DATE')

    @property
    def INTERNAL_BID(self):
        return self.get_aggregated_property('INTERNAL_BID')

    @property
    def CREATED_DATE(self):
        return self.get_aggregated_property('CREATED_DATE')


def import_from_file(filename):
    shots = dict()
    with open(filename, newline='') as import_file:
        dict_reader = csv.DictReader(import_file, delimiter='|')
        for row in dict_reader:
            s = Shot(project=row['PROJECT'],
                     shot=row['SHOT'],
                     version=row['VERSION'],
                     status=row['STATUS'],
                     finish_date=row['FINISH_DATE'],
                     internal_bid=row['INTERNAL_BID'],
                     created_date=row['CREATED_DATE'])

            shots[s.uid] = s

    return shots


def import_file_and_store(filename):
    shots = import_from_file(filename)
    pickle_dump(shots)


def pickle_dump(data, filename='output.pkl'):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle)


def pickle_load(filename):
    with open(filename, 'rb') as handle:
        data = pickle.load(handle)

    return list(data.values())


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parameter for the importer')
    parser.add_argument('-f', '--filename', nargs='+', help='file to import')
    args = parser.parse_args()
    import_file_and_store(args.filename[0])


if __name__ == '__main__':
    main()
