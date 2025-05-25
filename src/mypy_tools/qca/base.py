from abc import ABC, abstractmethod
from qcelemental.models.molecule import Molecule
from qcportal import PortalClient
from qcportal.dataset_models import BaseDataset
from typing import Optional


class BaseQCA(ABC):
    def __init__(self, address: str, port: int, username: str, password: str):
        try:
            self.client = PortalClient(
                f"{address}:{port}", username=username, password=password
            )
        except Exception as e:
            raise ConnectionError(f"Couldn't connect to QCArchive server: {e}")

    @abstractmethod
    def record_add(
        self,
        mols: Molecule | list[Molecule],
        program: str,
        method: str,
        basis: str,
        tag: str,
        **kwargs,
    ) -> list[int]:
        pass

    @abstractmethod
    def dataset_add(self, mols: Molecule | list[Molecule], name: str) -> BaseDataset:
        pass

    @abstractmethod
    def dataset_add_specification(
        self,
        dataset: BaseDataset,
        program: str,
        method: str,
        basis: str,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    def dataset_submit(
        self,
        dataset: BaseDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
    ) -> None:
        pass

    @abstractmethod
    def dataset_reset(
        self,
        dataset: BaseDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
        hard_reset: Optional[bool] = False,
    ) -> None:
        pass

    @abstractmethod
    def dataset_cancel(
        self, dataset: BaseDataset, specs: Optional[str | list[str]]
    ) -> None:
        pass

    @abstractmethod
    def dataset_check(
        self, dataset: BaseDataset, verbose: Optional[bool] = False
    ) -> None:
        pass

    @abstractmethod
    def dataset_store(
        self, dataset: BaseDataset, path: str, specs: Optional[str | list[str]]
    ) -> None:
        pass
