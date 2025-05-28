import qcelemental as qcel
from qcelemental.models.molecule import Molecule
from qcportal.singlepoint import SinglepointRecord, SinglepointDataset, QCSpecification
from typing import Optional
from .base import BaseQCA

import hashlib

h_2_kcalmol = qcel.constants.hartree2kcalmol
bohr_2_angstroms = qcel.constants.bohr2angstroms


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
        """Add a singlepoint calculation to the queue.

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
        self, mols: Molecule | list[Molecule], name: str
    ) -> SinglepointDataset:
        """Add a singlepoint dataset and entries to the client.

        Args:
            mols (Molecule | list[Molecule]): Molecule or list of molecules to add.
            name (str): Name of the dataset.

        Returns:
            None
        """
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
        """Add a specification to the dataset.

        Args:
            dataset (SinglepointDataset): Dataset to add the specification to.
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

        kwarg_hash = hashlib.md5(
            str(kwargs).encode()
        ).hexdigest()  # TODO: make work with nested kwargs

        dataset.add_specification(
            name=f"{program}/{method}/{basis}/{kwarg_hash}",
            specification=spec,
        )

        return kwarg_hash

    def dataset_submit(
        self,
        dataset: SinglepointDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
    ) -> None:
        """Submit a dataset to the client.

        Args:
            dataset (SinglepointDataset): Dataset to submit.
            tag (str): Tag to use for the submission.
            specs (str | list(str)): Specification(s) to use for the submission.

        Returns:
            None
        """
        dataset.submit(tag=tag, specification_names=specs)

    def dataset_reset(
        self,
        dataset: SinglepointDataset,
        tag: str,
        specs: Optional[str | list[str]] = None,
        hard_reset: bool = False,
    ) -> None:
        """Rerun a dataset.

        Args:
            dataset (SinglepointDataset): Dataset to rerun.
            tag (str): Tag to use for the rerun.
            specs (str | list(str)): Specification to use for the rerun.
            hard_reset (bool): Whether to fully delete the records

        Returns:
            None
        """
        if hard_reset:
            del_recs = []
            for _, _, rec in dataset.iterate_records(specification_names=specs):
                if rec.status == "ERROR":
                    del_recs.append(rec.id)

            self.client.delete_records(del_recs, soft_delete=False)
            dataset.submit(tag=tag, specification_names=specs)

        else:
            dataset.set_tags([tag])
            dataset.reset_records(specification_names=specs)

    def dataset_cancel(
        self, dataset: SinglepointDataset, specs: Optional[str | list[str]] = None
    ) -> None:
        """Cancel a dataset.

        Args:
            dataset (SinglepointDataset): Dataset to cancel.
            specs (str | list(str)): Specification(s) to cancel.

        Returns:
            None
        """
        dataset.cancel_records(specification_names=specs)

    def dataset_check(self, dataset: SinglepointDataset, verbose: bool = False) -> None:
        """Check the status of a dataset.

        Args:
            dataset (SinglepointDataset): Dataset to check.

        Returns:
            None
        """
        dataset.print_status()
        if verbose:
            for _, _, rec in dataset.iterate_records():
                print(f"Record {rec.id}: {rec.status}")
