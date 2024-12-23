import shutil, os

def copy_psi_template(
    name: str,
    system: str,
    method: str,
    basis: str,
    convergence: str,
    memory: str,
    charge: int = 0,
    template_path: str = '~/data/gits/mypy_tools/templates/psi.template',
) -> None:
    # Copy template input file to current directory
    shutil.copy(os.path.expanduser(template_path), f'./{name}.py')

    # Replace the template data with the actual data
    # Assumes that `system` is a psi-formatted geometry
    with open(f"{name}.py", 'r') as f:
        file_data = f.read()
        file_data = file_data.replace("MOL_DATA", system)
        file_data = file_data.replace("METHOD", method)
        file_data = file_data.replace("BASIS_SET", basis)
        file_data = file_data.replace("CONVERGENCE_TYPE", convergence)
        file_data = file_data.replace("JOB_MEM", memory)
        file_data = file_data.replace("CHARGE", charge)

    # Write the new file
    with open(f"{name}.py", 'w') as f:
        f.write(file_data)

# Slurm specific
def copy_sbatch_template(
    name: str,
    time: str,
    partition: str,
    template_path: str = '~/data/gits/mypy_tools/templates/sbatch.template',
    psi_build: str = 'build_dlpno_ccsd_t_vars',
    **kwargs,
) -> None:
    # Copy template input file to current directory
    shutil.copy(os.path.expanduser(template_path), f'./{name}.sbatch')

    job_name = name
    for k, v in kwargs.items():
        job_name += f'_{v}'

    # Replace the template data with the actual data
    with open(f'./{name}.sbatch', 'r') as f:
        file_data = f.read()
        file_data = file_data.replace('MY_JOB_NAME', job_name)
        file_data = file_data.replace('MOL_NAME', name)
        file_data = file_data.replace('SLURM_TIME', time)
        file_data = file_data.replace('SLURM_PARTITION', partition)
        file_data = file_data.replace('PSI4_BUILD', psi_build)

    # Write the new file
    with open(f'./{name}.sbatch', 'w') as f:
        f.write(file_data)

if __name__ == '__main__':
    pass
