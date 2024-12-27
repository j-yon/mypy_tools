def read_sacct(
    job_id: int,
    save_file: str = 'sacct.pkl',
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

    # Must contain non-empty DF to concat
    try:
        old_df = pd.read_pickle(save_file)
        if job_id in old_df['JobID'].values:
            print('Job ID already in DataFrame')
            return

        df = pd.concat([old_df, df])

    except IOError:
        pass

    df.to_pickle(save_file)

if __name__ == '__main__':
    pass
