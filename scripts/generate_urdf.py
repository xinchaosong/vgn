import os
import h5py
from tqdm import tqdm

from path import acronym_path, vgn_data_path

acronym_grasps_path = os.path.join(acronym_path, "grasps")

urdfs_path = os.path.join(vgn_data_path, "urdfs", "acronym")
urdfs_train_path = os.path.join(urdfs_path, "train")
urdfs_val_path = os.path.join(urdfs_path, "val")
urdfs_test_path = os.path.join(urdfs_path, "test")

with open("template.urdf", "r") as f:
    template_urdf = f.read()


def generate_urdf(dataset, dataset_path):
    print(dataset_path)

    for hdf5 in tqdm(dataset):
        hdf5_name = hdf5.strip()
        grasps = h5py.File(os.path.join(acronym_grasps_path, hdf5_name), 'r')

        obj_path = os.path.join(acronym_path, grasps['object/file'][()].decode('ascii'))
        obj_name = obj_path[obj_path.rfind("/") + 1:obj_path.rfind(".")]
        obj_mass = str(grasps['object/mass'][()])

        urdf = template_urdf.replace("obj_path", obj_path).replace("obj_name", obj_name).replace("obj_mass", obj_mass)
        urdf_name = hdf5_name[:hdf5_name.rfind(".")] + ".urdf"
        with open(os.path.join(dataset_path, urdf_name), "w") as uf:
            uf.writelines(urdf)


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
