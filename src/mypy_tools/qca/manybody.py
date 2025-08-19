import hashlib
import json

from qcelemental.models.molecule import Molecule
from qcportal.manybody import (
    BSSECorrectionEnum,
    ManybodyDataset,
    ManybodySpecification,
)
from qcportal.singlepoint import QCSpecification

from .base import BaseQCA


class ManybodyQCA(BaseQCA):
    def __init__(self, address: str, port: int, username: str, password: str):
        super().__init__(address, port, username, password)
        self.computation_type = "manybody"

    def record_add(
        self,
        mols: Molecule | list[Molecule],
        program: str,
        method: str,
        basis: str,
        tag: str,
        **kwargs,
    ) -> list[int]:
        spec = QCSpecification(
            program=program,
            driver="energy",
            method=method,
            basis=basis,
            keywords=kwargs,
        )
        _, ids = self.client.add_manybodys(
            mols,
            program="qcmanybody",
            bsse_correction=[BSSECorrectionEnum.cp],
            levels={
                1: spec,
                2: spec,
            },
            keywords={},
            tag=tag,
        )

        return ids

    def dataset_add(
        self,
        name: str,
        mols: Molecule | list[Molecule],
    ) -> ManybodyDataset:
        dataset = self.client.add_dataset(
            dataset_type="manybody",
            name=name,
            description=f"Manybody dataset for {name}",
        )

        if isinstance(mols, Molecule):
            mols = [mols]

        for mol in mols:
            dataset.add_entry(
                name=mol.name,
                molecule=mol,
            )

        return dataset

    def dataset_add_specification(
        self,
        dataset: ManybodyDataset,
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

        # assuming only dimer calculations for now
        manybody_spec = ManybodySpecification(
            program="qcmanybody",
            bsse_correction=[BSSECorrectionEnum.cp],
            levels={
                1: spec,
                2: spec,
            },
        )

        kwarg_str = json.dumps(kwargs, sort_keys=True)
        kwarg_hash = hashlib.md5(
            kwarg_str.encode()
        ).hexdigest()  # TODO: make work with nested kwargs

        spec_name = f"{program}/{method}/{basis}/{kwarg_hash}"

        dataset.add_specification(
            name=spec_name,
            specification=manybody_spec,
        )

        return spec_name
