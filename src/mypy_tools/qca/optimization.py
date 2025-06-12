import hashlib
import json

from qcelemental.models.molecule import Molecule
from qcportal.singlepoint import QCSpecification
from qcportal.optimization import (
    OptimizationDataset,
    OptimizationSpecification,
)
from typing import Optional
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
        """Add a optimization calculation to the queue.

        Args:
            mols (Molecule | list[Molecule]): Molecule or list of molecules to add.
            program (str): Program to use for the calculation.
            method (str): Method to use for the calculation.
            basis (str): Basis set to use for the calculation.
            tag (str): Tag to use for the calculation.
            **kwargs: Additional arguments to pass to the calculation.

        Returns:
            None
        """
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
        self, mols: Molecule | list[Molecule], name: str
    ) -> OptimizationDataset:
        """Add an optimization dataset and entries to the client.

        Args:
            mols (Molecule | list[Molecule]): Molecule or list of molecules to add.
            name (str): Name of the dataset.

        Returns:
            None
        """
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
        """Add a specification to the dataset.

        Args:
            dataset (OptimizationDataset): Dataset to add the specification to.
            program (str): Program to use for the calculation.
            method (str): Method to use for the calculation.
            basis (str): Basis set to use for the calculation.
            **kwargs: Additional arguments to pass to the calculation.

        Returns:
            Hash of the specification.
        """
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

    def dataset_submit(
        self,
        dataset: OptimizationDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
    ) -> None:
        """Submit a dataset to the client.

        Args:
            dataset (OptimizationDataset): Dataset to submit.
            tag (str): Tag to use for the submission.
            specs (str | list(str)): Specification(s) to use for the submission.

        Returns:
            None
        """
        dataset.submit(tag=tag, specification_names=specs)

    def dataset_reset(
        self,
        dataset: OptimizationDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
        hard_reset: bool = False,
    ) -> None:
        """Rerun a dataset.

        Args:
            dataset (OptimizationDataset): Dataset to rerun.
            tag (str): Tag to use for the rerun.
            specs (str | list(str)): Specification to use for the rerun.
            hard_reset (bool): Whether to fully delete the records

        Returns:
            None
        """
        if hard_reset:
            for _, _, rec in dataset.iterate_records(
                status=["error", "cancelled"],
                specification_names=specs,
            ):
                self.client.delete_records(
                    rec.id, soft_delete=False
                )  # will also delete child records
            self.dataset_check(dataset, verbose=True)
            dataset.submit(tag=tag, specification_names=specs)

        else:
            dataset.set_tags([tag])
            dataset.reset_records(specification_names=specs)

    def dataset_cancel(
        self, dataset: OptimizationDataset, specs: Optional[str | list[str]] = None
    ) -> None:
        """Cancel a dataset.

        Args:
            dataset (OptimizationDataset): Dataset to cancel.
            specs (str | list(str)): Specification(s) to cancel.

        Returns:
            None
        """
        dataset.cancel_records(specification_names=specs)

    def dataset_check(
        self,
        dataset: OptimizationDataset,
        specs: Optional[str | list[str]] = None,
        verbose: Optional[bool] = False,
    ) -> None:
        """Check the status of a dataset.

        Args:
            dataset (OptimizationDataset): Dataset to check.

        Returns:
            None
        """
        dataset.print_status()
        if verbose:
            for _, _, rec in dataset.iterate_records(specification_names=specs):
                print(f"Record {rec.id}: {rec.status}")
