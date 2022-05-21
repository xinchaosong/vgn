from pathlib import Path

import h5py

data_path = Path(__file__).resolve().parent.parent / "data"
acronym_path = data_path / "acronym" / "grasps"
vgnized_dataset_path = data_path / "urdfs" / "acronym"

with open("template.urdf", "r") as f:
    urdf_lines = f.readlines()

grasps = h5py.File(acronym_path / 'WineGlass_2d89d2b3b6749a9d99fbba385cc0d41d_0.0024652679182251653.h5', 'r')

obj_name = grasps['object/file'][()].decode('ascii')
obj_name = obj_name[obj_name.rfind("/") + 1:]
obj_mass = grasps['object/mass'][()]

for i in range(len(urdf_lines)):
    urdf_lines[i] = urdf_lines[i].replace("obj_name.obj", obj_name)
    urdf_lines[i] = urdf_lines[i].replace("obj_mass", str(obj_mass))

urdf_name = obj_name[:-4] + ".urdf"

with open(vgnized_dataset_path / urdf_name, "w") as f:
    f.writelines(urdf_lines)
