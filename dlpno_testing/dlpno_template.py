import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

nthreads = 8

memory 200 gb

molecule MOL_NAME {
MOL_DATA
units angstrom
no_com
no_reorient
}

set {
    E_CONVERGENCE 8
    D_CONVERGENCE 8
    scf_type df
    mp2_type df
    cc_type df
    freeze_core True
    pno_convergence CONVERGENCE_TYPE
}

set_num_threads(nthreads)
energy('dlpno-ccsd/BASIS_SET')

with open("vars.json", "w") as f:
     json_dump = json.dumps(psi4.core.variables(), indent=4, cls=NumpyEncoder)
     f.write(json_dump)
