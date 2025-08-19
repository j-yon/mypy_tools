from abc import ABC, abstractmethod

from qcelemental.models.molecule import Molecule
from qcportal import PortalClient
from qcportal.dataset_models import BaseDataset


class BaseQCA(ABC):
    """Base class for QCArchive clients."""

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
        """Add a new record to the queue.

        Args:
            mols (Molecule | list[Molecule]): Molecule or list of molecules to add.
            program (str): Program to use for the calculation.
            method (str): Method to use for the calculation.
            basis (str): Basis set to use for the calculation.
            tag (str): Tag to use for the calculation.
            **kwargs: Additional arguments to pass to the calculation.

        Returns:
            list[int]: List of record IDs added.
        """
        pass

    @abstractmethod
    def dataset_add(
        self,
        name: str,
        mols: Molecule | list[Molecule],
    ) -> BaseDataset:
        """Add a new dataset with Molecule entries to the client.

        Args:
            name (str): Name of the dataset.
            mols (Molecule | list[Molecule]): Molecule or list of molecules to add.

        Returns:
            BaseDataset: The created dataset.
        """
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
        """Add a specification to the given dataset.

        Args:
            dataset (BaseDataset): Dataset to add the specification to.
            program (str): Program to use for the calculation.
            method (str): Method to use for the calculation.
            basis (str): Basis set to use for the calculation.
            **kwargs: Additional arguments to pass as keywords.

        Returns:
            str: Name of the specification.
        """
        pass
