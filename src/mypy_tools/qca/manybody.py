import hashlib
import json

from qcelemental.models.molecule import Molecule
from qcportal.singlepoint import QCSpecification
from qcportal.manybody import (
    ManybodyDataset,
    ManybodySpecification,
    BSSECorrectionEnum,
)
from qcportal.record_models import RecordStatusEnum
from typing import Optional
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
        """Add a manybody calculation to the queue.

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
        self, mols: Molecule | list[Molecule], name: str
    ) -> ManybodyDataset:
        """Add a manybody dataset and entries to the client.

        Args:
            mols (Molecule | list[Molecule]): Molecule or list of molecules to add.
            name (str): Name of the dataset.

        Returns:
            None
        """
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
        """Add a specification to the dataset.

        Args:
            dataset (ManybodyDataset): Dataset to add the specification to.
            program (str): Program to use for the calculation.
            method (str): Method to use for the calculation.
            basis (str): Basis set to use for the calculation.
            **kwargs: Additional arguments to pass to the calculation.

        Returns:
            Name of the specification
        """
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

    # kinda useless atm
    def dataset_submit(
        self,
        dataset: ManybodyDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
    ) -> None:
        """Submit a dataset to the client.

        Args:
            dataset (ManybodyDataset): Dataset to submit.
            tag (str): Tag to use for the submission.
            specs (str | list(str)): Specification(s) to use for the submission.

        Returns:
            None
        """
        dataset.submit(tag=tag, specification_names=specs)

    def dataset_reset(
        self,
        dataset: ManybodyDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
        hard_reset: Optional[bool] = False,
    ) -> None:
        """Rerun a dataset.

        Args:
            dataset (ManybodyDataset): Dataset to rerun.
            tag (str): Tag to use for the rerun.
            specs (str | list(str)): Specification(s) to use for the rerun.
            hard_reset (bool): Whether to fully delete the records

        Returns:
            None
        """
        if hard_reset:
            for _, _, rec in dataset.iterate_records(
                status=[RecordStatusEnum.error, RecordStatusEnum.cancelled],
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

    # kinda useless atm
    def dataset_cancel(
        self, dataset: ManybodyDataset, specs: Optional[str | list[str]] = None
    ) -> None:
        """Cancel a dataset.

        Args:
            dataset (ManybodyDataset): Dataset to cancel.
            specs (str | list(str)): Specification(s) to cancel.

        Returns:
            None
        """
        dataset.cancel_records(specification_names=specs)

    def dataset_check(
        self,
        dataset: ManybodyDataset,
        specs: Optional[str | list[str]] = None,
        verbose: Optional[bool] = False,
    ) -> None:
        """Check the status of a dataset.

        Args:
            dataset (ManybodyDataset): Dataset to check.
            verbose (bool): Whether to print detailed record status.

        Returns:
            None
        """
        dataset.print_status()
        if verbose:
            for _, _, rec in dataset.iterate_records(specification_names=specs):
                print(f"Record {rec.id}: {rec.status}")
