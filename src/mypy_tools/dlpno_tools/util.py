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
    save_file: str = None,
    **kwargs,
) -> None:
    import subprocess
    import pandas as pd

    def split_by_idx(s, indices):
        left, right = 0, indices[0]
        yield s[left:right]
        left = right
        for right in indices[1:]:
            yield s[left:right] 
            left = right
        yield s[left:]

    # Execute sacct command
    sacct = subprocess.run(['sacct', '-j', str(job_id)], check=True, capture_output=True, text=True).stdout.splitlines()
    # sacct[0] == column headers
    # sacct[1] == separating dashes
    # sacct[2] == sacct info (except MaxRSS, that will be in sacct[3])

    # Parse data from sacct output
    columns = sacct[0].split()
    indices = [i for i, char in enumerate(list(sacct[1])) if char == ' ']
    df_to_be = {key : item.strip() for key, item in zip(columns, split_by_idx(sacct[2], indices))}

    # Get MaxRSS data since that isn't kept in first line
    # get index of maxrss in column list
    # get actual indices from indices, split_by_idx
    # place value (stripped) in df to be
    if 'MaxRSS' in columns:
        maxRSS_index = columns.index('MaxRSS')
        df_to_be['MaxRSS'] = sacct[3][indices[maxRSS_index - 1]:indices[maxRSS_index]].strip()

    # Add extra information like job parameters that aren't defined in sacct output
    for k, v in kwargs.items():
        df_to_be[k] = v

    df = pd.DataFrame(df_to_be, index=[0])
    if save_file is not None:
        # Must contain non-empty DF to concat
        df = pd.concat(pd.read_pkl(save_file), pd.DataFrame(df_to_be))

    df.to_pickle('sacct.pkl')

if __name__ == '__main__':
    pass
