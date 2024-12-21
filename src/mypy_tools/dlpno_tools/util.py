def copy_dlpno_template(
    name: str,
    system: str,
    basis: str,
    convergence: str,
    memory: str,
    template_path: str = None,
) -> None:
    import shutil

    # copy template input file to current directory
    shutil.copy(template_path, f'./{name}.py')

    # replace the template data with the actual data
    # assumes that `system` is a properly formatted psi input
    with open(f"{name}.py", 'r') as f:
        file_data = f.read()
        file_data = file_data.replace("MOL_NAME", name)
        file_data = file_data.replace("MOL_DATA", system)
        file_data = file_data.replace("BASIS_SET", basis)
        file_data = file_data.replace("CONVERGENCE_TYPE", convergence)
        file_data = file_data.replace("JOB_MEM", memory)

    # write the new file
    with open(f"{name}.py", 'w') as f:
        f.write(file_data)

# Slurm specific
def read_sacct(
    job_id: int,
) -> None:
    import subprocess

    sacct = subprocess.check_output(['sacct', '-j', job_id])
    print(sacct)

if __name__ == '__main__':
    pass
