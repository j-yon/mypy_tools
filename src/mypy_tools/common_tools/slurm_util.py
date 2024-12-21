def copy_sbatch(
    name: str,
    time: str,
    partition: str,
    template_path: str = None,
    psi_build: str = 'build_dlpno_ccsd_t_vars',
) -> None:
    import shutil

    assert template_path is not None, 'Must provide a template path'

    shutil.copy(template_path, f'./{name}.sbatch')
    with open('./submit.sbatch', 'r') as f:
        file_data = f.read()
        file_data = file_data.replace('MOL_NAME', name)
        file_data = file_data.replace('SLURM_TIME', time)
        file_data = file_data.replace('SLURM_PARTITION', partition)

    with open(f'./{name}.sbatch', 'w') as f:
        f.write(file_data)

if __name__ == '__main__':
    pass
