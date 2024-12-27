import shutil, os

def __replace_options(data, options):
    for k, v in options.items():
        if k == '__psi_options':
            psi_opts = ''.join([f"{k} {v}\n" for k, v in options['__psi_options'].items()])
            data = data.replace("__psi_options", psi_opts)
            continue

        if type(v) == dict:
            data = __replace_options(data, v)

        data = data.replace(k, str(v))

    return data

def copy_psi_template(
    json_input: dict,
    template_path: str = '~/data/gits/mypy_tools/templates/psi.template',
) -> None:
    # Copy template input file to current directory
    shutil.copy(os.path.expanduser(template_path), f'./{json_input["__name"]}.py')

    # def replace_options(data, options):
    #     for k, v in options.items():
    #         if k == '__psi_options':
    #             psi_opts = ''.join([f"{k} {v}\n" for k, v in json_input['__psi_options'].items()])
    #             data = data.replace("__psi_options", psi_opts)
    #             continue
    #
    #         if type(v) == dict:
    #             data = replace_options(data, v)
    #
    #         data = data.replace(k, str(v))
    #
    #     return data

    # Replace the template data with the actual data
    with open(f'{json_input["__name"]}.py', 'r') as f:
        file_data = __replace_options(f.read(), json_input)
        # file_data = file_data.replace("GEOMETRY", json_input['xyz'])
        # file_data = file_data.replace("METHOD", json_input['method'])
        # file_data = file_data.replace("BASIS_SET", json_input['basis'])
        # file_data = file_data.replace("JOB_MEM", json_input['memory'])


    # Write the new file
    with open(f'{json_input["__name"]}.py', 'w') as f:
        f.write(file_data)

# Slurm specific
def copy_sbatch_template(
    json_input: dict,
    template_path: str = '~/data/gits/mypy_tools/templates/sbatch.template',
) -> None:
    # Copy template input file to current directory
    shutil.copy(os.path.expanduser(template_path), f'./{json_input["__name"]}.sbatch')

    json_input['__job_name'] = json_input['__name']
    for k, v in json_input['__kwargs'].items():
        job_name += f'_{v}'

    # Replace the template data with the actual data
    with open(f'{json_input["__name"]}.sbatch', 'r') as f:
        file_data = __replace_options(f.read(), json_input)
    # # Replace the template data with the actual data
    # with open(f'./{json_input["__name"]}.sbatch', 'r') as f:
    #     file_data = f.read()
    #     file_data = file_data.replace('MY_JOB_NAME', job_name)
    #     file_data = file_data.replace('MOL_NAME', json_input['name'])
    #     file_data = file_data.replace('SLURM_TIME', json_input['slurm_options']['time'])
    #     file_data = file_data.replace('SLURM_PARTITION', json_input['slurm_options']['partition'])
    #     file_data = file_data.replace('PSI4_BUILD', json_input['psi_build'])
    # Replace the template data with the actual data

    # Write the new file
    with open(f'./{json_input["__name"]}.sbatch', 'w') as f:
        f.write(file_data)

if __name__ == '__main__':
    pass
