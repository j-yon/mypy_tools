#!/usr/bin/env python3

import sys, subprocess

def copy_dlpno_template(
    name: str,
    system: str,
    basis: str,
    convergence: str,
) -> None:
    # copy template input file to current directory
    subprocess.run(['cp', '/theoryfs2/ds/jadeny/scripts/dlpno_testing/dlpno_template.py', f'./{name}.py'])

    # replace the template data with the actual data
    # assumes that `system` is a properly formatted psi input
    with open(f"{name}.py", 'r') as f2:
        file_data = f2.read()
        file_data = file_data.replace("MOL_NAME", name)
        file_data = file_data.replace("MOL_DATA", system)
        file_data = file_data.replace("BASIS_SET", basis)
        file_data = file_data.replace("CONVERGENCE_TYPE", convergence)

    # write the new file
    with open(f"{name}.py", 'w') as f3:
        f3.write(file_data)

