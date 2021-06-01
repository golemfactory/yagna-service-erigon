from dataclasses import dataclass
from yapapi.props import inf
from yapapi.props.base import constraint
from yapapi.payload import Payload

ERIGON_RUNTIME_NAME = "ttt"


@dataclass
class ErigonPayload(Payload):
    runtime: str = constraint(inf.INF_RUNTIME_NAME, "=", ERIGON_RUNTIME_NAME)
    min_mem_gib: float = constraint(inf.INF_MEM, ">=", 0.5)
    min_storage_gib: float = constraint(inf.INF_STORAGE, ">=", 0.5)
