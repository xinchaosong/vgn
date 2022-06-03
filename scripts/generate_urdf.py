import os
from pathlib import Path
import h5py

acronym_path = "/media/DATACENTER2/HiLo_other_approaches/Acronym/"
acronym_grasps_path = os.path.join(acronym_path, "grasps")

urdfs_path = Path(__file__).resolve().parent.parent / "data" / "urdfs" / "acronym"
urdfs_train_path = str(urdfs_path / "train")
urdfs_val_path = str(urdfs_path / "val")
urdfs_test_path = str(urdfs_path / "test")

with open("template.urdf", "r") as f:
    template_urdf_lines = f.readlines()


def generate_urdf(dataset, dataset_path):
    for hdf5 in dataset:
        hdf5_name = hdf5.strip()
        grasps = h5py.File(os.path.join(acronym_grasps_path, hdf5_name), 'r')

        obj_name = grasps['object/file'][()].decode('ascii')
        obj_name = obj_name[obj_name.rfind("/") + 1:obj_name.rfind(".")]
        obj_mass = grasps['object/mass'][()]

        urdf_lines = template_urdf_lines.copy()
        for i in range(len(urdf_lines)):
            urdf_lines[i] = urdf_lines[i].replace("obj_name", obj_name)
            urdf_lines[i] = urdf_lines[i].replace("obj_mass", str(obj_mass))

        urdf_name = hdf5_name[:hdf5_name.rfind(".") + 1:] + ".urdf"

        with open(os.path.join(dataset_path, urdf_name), "w") as f:
            f.writelines(urdf_lines)


with open(os.path.join(acronym_path, "train_set.txt"), "r") as f:
    train_set = f.readlines()

if not os.path.exists(urdfs_train_path):
    os.mkdir(urdfs_train_path)

generate_urdf(train_set, urdfs_train_path)

with open(os.path.join(acronym_path, "val_set.txt"), "r") as f:
    val_set = f.readlines()

if not os.path.exists(urdfs_val_path):
    os.mkdir(urdfs_val_path)

generate_urdf(val_set, urdfs_val_path)

with open(os.path.join(acronym_path, "test_set.txt"), "r") as f:
    test_set = f.readlines()

if not os.path.exists(urdfs_test_path):
    os.mkdir(urdfs_test_path)

generate_urdf(test_set, urdfs_test_path)
