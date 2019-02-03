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

    @classmethod
    def from_csv_row(cls, row):
        return cls(
            project=row['PROJECT'],
            shot=row['SHOT'],
            version=int(row['VERSION']),
            status=row['STATUS'],
            finish_date=row['FINISH_DATE'],
            internal_bid=float(row['INTERNAL_BID']),
            created_date=row['CREATED_DATE']
        )

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
    DEFAULT = (None, lambda s: s[0])

    def __call__(self, *args, **kwargs):
        return self.value[1](*args, **kwargs)

    @classmethod
    def from_string(cls, s):
        for c in cls:
            if c.value[0] == s:
                return c

        print(f'{cls.__name__} has no value matching "{s}", using DEFAULT')
        return Aggregation.DEFAULT


class ShotGroup:
    def __init__(self, shots: list, aggregrations: dict):
        self.shots = shots
        self.aggregating_method = dict()

        for k, v in aggregrations.items():
            self.aggregating_method[k] = Aggregation.from_string(v)

    def get_properity(self, property):
        return [getattr(s, property) for s in self.shots]

    def get_aggregated_property(self, property):
        aggregating_method = self.aggregating_method.get(property, Aggregation.DEFAULT)
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
