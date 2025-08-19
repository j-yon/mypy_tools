import hashlib
import json

from qcelemental.models.molecule import Molecule
from qcportal.singlepoint import QCSpecification, SinglepointDataset

from .base import BaseQCA


class SinglepointQCA(BaseQCA):
    def __init__(self, address: str, port: int, username: str, password: str):
        super().__init__(address, port, username, password)
        self.computation_type = "singlepoint"

    def record_add(
        self,
        mols: Molecule | list[Molecule],
        program: str,
        method: str,
        basis: str,
        tag: str,
        **kwargs,
    ) -> list[int]:
        _, ids = self.client.add_singlepoints(
            mols,
            program=program,
            driver="energy",
            method=method,
            basis=basis,
            keywords=kwargs,
            tag=tag,
        )

        return ids

    def dataset_add(
        self,
        name: str,
        mols: Molecule | list[Molecule],
    ) -> SinglepointDataset:
        dataset = self.client.add_dataset(
            dataset_type="singlepoint",
            name=name,
            description=f"Singlepoint dataset for {name}",
        )

        if isinstance(mols, Molecule):
            mols = [mols]

        for mol in mols:
            dataset.add_entry(
                name=mol.name,
                molecule=mol,
                comment="",
            )

        return dataset

    def dataset_add_specification(
        self,
        dataset: SinglepointDataset,
        program: str,
        method: str,
        basis: str,
        **kwargs,
    ) -> str:
        spec = QCSpecification(
            program=program,
            driver="energy",
            method=method,
            basis=basis,
            keywords=kwargs,
        )

        kwarg_str = json.dumps(kwargs, sort_keys=True)
        kwarg_hash = hashlib.md5(
            kwarg_str.encode()
        ).hexdigest()  # TODO: make work with nested kwargs

        spec_name = f"{program}/{method}/{basis}/{kwarg_hash}"

        dataset.add_specification(
            name=spec_name,
            specification=spec,
        )

        return spec_name
