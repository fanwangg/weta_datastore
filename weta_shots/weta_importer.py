import csv
import pickle

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
        return (self.project, self.shot, self.version)


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


def pickle_dump(data, filename='output.pkl'):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle)


def pickle_load(filename):
    with open(filename, 'rb') as handle:
        data = pickle.load(handle)
    return data


def import_file_and_store(filename):
    shots = import_from_file(filename)
    pickle_dump(shots)
