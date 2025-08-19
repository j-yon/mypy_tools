import hashlib
import json

from qcelemental.models.molecule import Molecule
from qcportal.optimization import (
    OptimizationDataset,
    OptimizationSpecification,
)
from qcportal.singlepoint import QCSpecification

from .base import BaseQCA


class OptimizationQCA(BaseQCA):
    def __init__(self, address: str, port: int, username: str, password: str):
        super().__init__(address, port, username, password)
        self.computation_type = "optimization"

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
        _, ids = self.client.add_optimizations(
            mols,
            program="optking",
            qc_specification=spec,
            tag=tag,
        )

        return ids

    def dataset_add(
        self,
        name: str,
        mols: Molecule | list[Molecule],
    ) -> OptimizationDataset:
        dataset = self.client.add_dataset(
            dataset_type="optimization",
            name=name,
            description=f"Optimization dataset for {name}",
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
        dataset: OptimizationDataset,
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

        opt_spec = OptimizationSpecification(
            program="optking",
            qc_specification=spec,
        )

        kwarg_str = json.dumps(kwargs, sort_keys=True)
        kwarg_hash = hashlib.md5(
            kwarg_str.encode()
        ).hexdigest()  # TODO: make work with nested kwargs

        spec_name = f"{program}/{method}/{basis}/{kwarg_hash}"

        dataset.add_specification(
            name=spec_name,
            specification=opt_spec,
        )

        return spec_name
