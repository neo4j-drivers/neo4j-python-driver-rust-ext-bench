import abc
import os
import typing as t
from dataclasses import dataclass
from timeit import default_timer as timer

import neo4j


URL = os.environ.get("NEO4J_URL", "neo4j://localhost:7687")
AUTH_USER = os.environ.get("NEO4J_USER", "neo4j")
AUTH_PASS = os.environ.get("NEO4J_PASS", "pass")
AUTH = (AUTH_USER, AUTH_PASS)
DB = "neo4j"


QUERY_DESERIALIZE = """
UNWIND range(1, $length) AS _
RETURN [
    _ IN range(1, $width)
    | "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMM"
] AS x
"""

QUERY_SERIALIZE = """
RETURN 1
"""


class Work(abc.ABC):
    def __init__(self: t.Self, width: int, length: int) -> None:
        self.width = width
        self.length = length

    @abc.abstractmethod
    def run(self: t.Self, driver: neo4j.Driver, repetition: int) -> float:
        raise NotImplementedError()


class WorkDeserialize(Work):
    def run(self: t.Self, driver: neo4j.Driver, repetition: int) -> float:
        start = timer()
        for _ in range(repetition):
            driver.execute_query(
                QUERY_DESERIALIZE,
                database_=DB,
                width=self.width,
                length=self.length,
            )
        end = timer()
        elapsed = end - start
        return elapsed


class WorkSerialize(Work):
    def run(self: t.Self, driver: neo4j.Driver, repetition: int) -> float:
        data_inner = ["qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMM"]
        data_inner *= self.width
        data = [data_inner] * self.length
        start = timer()
        for _ in range(repetition):
            driver.execute_query(
                QUERY_SERIALIZE,
                database_=DB,
                data=data,
            )
        end = timer()
        elapsed = end - start
        return elapsed


def work_deserialize(driver: neo4j.Driver, width: int, length: int) -> None:
    driver.execute_query(
        QUERY_DESERIALIZE,
        database_=DB,
        width=width,
        length=length,
    )


@dataclass
class Workload:
    name: str
    work: t.Type[Work]
    width: int
    length: int
    repetition: int


WORKLOADS = (
    Workload("1x1_de", WorkDeserialize, 1, 1, 100),
    Workload("10x1_de", WorkDeserialize, 10, 1, 100),
    Workload("100x1_de", WorkDeserialize, 100, 1, 100),
    Workload("1000x1_de", WorkDeserialize, 1000, 1, 100),
    Workload("10000x1_de", WorkDeserialize, 10000, 1, 100),
    Workload("100000x1_de", WorkDeserialize, 100000, 1, 100),
    Workload("1x10_de", WorkDeserialize, 1, 10, 100),
    Workload("1x100_de", WorkDeserialize, 1, 100, 100),
    Workload("1x1000_de", WorkDeserialize, 1, 1000, 100),
    Workload("1x10000_de", WorkDeserialize, 1, 10000, 100),
    Workload("1x1_se", WorkSerialize, 1, 1, 1000),
    Workload("10x1_se", WorkSerialize, 10, 1, 1000),
    Workload("100x1_se", WorkSerialize, 100, 1, 1000),
    Workload("1000x1_se", WorkSerialize, 1000, 1, 1000),
    Workload("10000x1_se", WorkSerialize, 10000, 1, 1000),
    Workload("1x10_se", WorkSerialize, 1, 10, 1000),
    Workload("1x100_se", WorkSerialize, 1, 100, 1000),
    Workload("1x1000_se", WorkSerialize, 1, 1000, 1000),
    Workload("1x10000_se", WorkSerialize, 1, 10000, 1000),
)


def main() -> None:
    print("name,took")
    with neo4j.GraphDatabase.driver(URL, auth=AUTH) as driver:
        driver.verify_connectivity()
        for workload in WORKLOADS:
            work = workload.work(workload.width, workload.length)
            # warm-up
            work.run(driver, 20)

            elapsed = work.run(driver, workload.repetition)
            print(f"{workload.name},{elapsed}")


if __name__ == "__main__":
    main()
