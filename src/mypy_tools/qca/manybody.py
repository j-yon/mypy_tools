import hashlib
import qcelemental as qcel
from qcelemental.models.molecule import Molecule
from qcportal.singlepoint import QCSpecification
from qcportal.manybody import (
    ManybodyRecord,
    ManybodyDataset,
    ManybodySpecification,
    BSSECorrectionEnum,
)
from typing import Optional
from .base import BaseQCA

h_2_kcalmol = qcel.constants.hartree2kcalmol
bohr_2_angstroms = qcel.constants.bohr2angstroms


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
            Hash of the specification.
        """
        spec = QCSpecification(
            program=program,
            driver="energy",
            method=method,
            basis=basis,
            keywords=kwargs,
        )

        manybody_spec = ManybodySpecification(
            program="qcmanybody",
            bsse_correction=[BSSECorrectionEnum.cp],
            levels={
                1: spec,
                2: spec,
            },
        )

        kwarg_hash = hashlib.md5(
            str(kwargs).encode()
        ).hexdigest()  # TODO: make work with nested kwargs

        dataset.add_specification(
            name=f"{program}/{method}/{basis}/{kwarg_hash}",
            specification=manybody_spec,
        )

        return kwarg_hash

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
        hard_reset: bool = False,
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
            del_recs = []
            for _, _, rec in dataset.iterate_records(specification_names=specs):
                if rec.status == "ERROR" or rec.status == "CANCELED":
                    del_recs.append(rec.id)

            self.client.delete_records(
                del_recs, soft_delete=False
            )  # will also delete child records
            dataset.submit(tag=tag, specification_names=specs)

        else:
            dataset.set_tags([tag])
            dataset.reset_records(specification_names=specs)

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

    def dataset_check(self, dataset: ManybodyDataset, verbose: bool = False) -> None:
        """Check the status of a dataset.

        Args:
            dataset (ManybodyDataset): Dataset to check.

        Returns:
            None
        """
        dataset.print_status()
        if verbose:
            for _, _, rec in dataset.iterate_records():
                print(f"Record {rec.id}: {rec.status}")

    def dataset_store(
        self,
        dataset: ManybodyDataset,
        path: str,
        specs: Optional[str | list[str]] = None,
    ) -> None:
        """Store a dataset to a pickle file.

        Args:
            dataset (ManybodyDataset): Dataset to store.
            path (str): Path to store the dataset.

        Returns:
            None
        """

        def _assemble_data(rec: ManybodyRecord) -> tuple:
            rec_dict = rec.dict()

            props = rec_dict["properties"]
            clusters = rec_dict["clusters"]

            interaction_energy = (
                props["results"]["cp_corrected_interaction_energy"] * h_2_kcalmol
            )

            for cluster in clusters:
                pass  # TODO: add info from singlepoints
                # single_rec = cluster.singlepoint_record.dict()

            return (
                rec_dict["initial_molecule"],
                rec_dict["initial_molecule"]["atomic_numbers"],
                rec_dict["initial_molecule"]["geometry"],
                int(rec_dict["initial_molecule"]["molecular_charge"]),
                int(rec_dict["initial_molecule"]["molecular_multiplicity"]),
                interaction_energy,
            )

        df = dataset.compile_values(
            value_call=_assemble_data,
            value_names=[
                "Initial Molecule",
                "Atomic Numbers",
                "Geometry",
                "Charge",
                "Multiplicity",
                "CP Interaction Energy",
            ],
            specification_names=specs,
            unpack=True,
        )

        df.to_pickle(path)


# def add_MB_dataset(
#     client: PortalClient,
#     system: str,
# ) -> None:
#     """
#     Add a dataset with molecules and specification to client
#
#     Must be in a directory with input files to read from (at least to get Molecule entries)
#     """
#     from qcportal.manybody import ManybodyDatasetEntry
#     from qcelemental.models import Molecule
#
#     try:
#         ds = client.add_dataset("manybody", system, f"Dataset to contain manybody calculations on {system} crystal")
#         print(f"Added {system} as dataset")
#
#     except Exception:
#         print(f"{system} dataset already exists!")
#         sys.exit(1)
#
#     total_files = len([file for file in os.listdir(os.getcwd())])
#     entry_list = []
#     for io_file in next(os.walk(os.getcwd()))[2]:
#         if not io_file.endswith(".in") and not io_file.endswith(".out"):
#             continue
#
#         with open(io_file, "r") as f:
#             # not sure if theres a better way to do this, I'm just reading through the input file until I find keywords that denote where the geometry info is located
#             data = f.readlines()
#             search_idxs, found_idxs = set(["start", "end", "extras"]), set() # also kinda weird, just used to break early from file
#             for idx, line in enumerate(data):
#                 if line.startswith("# PSI4 file produced by CrystaLattE"):
#                     extras_idx = idx + 3
#                     found_idxs.add("extras")
#                 elif line.startswith("molecule"):
#                     start_idx = idx + 1
#                     found_idxs.add("start")
#                 elif line.startswith("units = au"):
#                     end_idx = idx
#                     found_idxs.add("end")
#
#                 if found_idxs == search_idxs:
#                     break
#
#             geom = "".join(data[start_idx:end_idx])
#
#             extras = data[extras_idx : extras_idx + 9]
#             extras_keys = ["N-mer Name", "Fragments", "Num. Rep. (#)", "COM Priority", "Min. COM Sep. (A)", "Sep. Priority", "Min. Sep. (A)", "Cut Priority", "V_NN"]
#             extras = {k: v.split(":")[1].strip() for k, v in zip(extras_keys, extras)}
#             name = extras["N-mer Name"]
#
#         mol = Molecule.from_data(
#             f"""
#                 {geom}
#                 units au
#                 no_reorient
#                 no_com
#                 symmetry c1
#             """,
#             dtype="psi4",
#             extras=extras,
#         )
#         ent = ManybodyDatasetEntry(name=name, initial_molecule=mol)
#         entry_list.append(ent)
#
#     ds.add_entries(entry_list)
#     print("Added molecules to dataset")
#     return
