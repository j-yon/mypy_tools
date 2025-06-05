from abc import ABC, abstractmethod
from qcelemental.models.molecule import Molecule
from qcportal import PortalClient
from qcportal.dataset_models import BaseDataset
from typing import Optional


class BaseQCA(ABC):
    def __init__(self, address: str, port: int, username: str, password: str):
        try:
            self.__client = PortalClient(
                f"{address}:{port}", username=username, password=password
            )
        except Exception as e:
            raise ConnectionError(f"Couldn't connect to QCArchive server: {e}")

        self.__computation_type = None

    @property
    def client(self) -> PortalClient:
        return self.__client

    @client.setter
    def client(self, client: PortalClient) -> None:
        self.__client = client

    @property
    def computation_type(self) -> str:
        if self.__computation_type is None:
            raise ValueError("Computation type is not set.")
        return self.__computation_type

    @computation_type.setter
    def computation_type(self, value: str) -> None:
        self.__computation_type = value

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
        self,
        dataset: BaseDataset,
        specs: Optional[str | list[str]] = None,
        verbose: Optional[bool] = False,
    ) -> None:
        pass
