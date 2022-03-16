import argparse
from pathlib import Path

from mpi4py import MPI
import numpy as np
import open3d as o3d
from tqdm import tqdm

from robot_helpers.io import load_yaml
from robot_helpers.spatial import Rotation, Transform
import vgn.database as db
from vgn.samplers import UniformPointCloudSampler
from vgn.perception import create_tsdf
from vgn.simulation import GraspSim, get_metric
from vgn.utils import find_urdfs, view_on_sphere


def main():
    worker_count, rank = setup_mpi()
    args = parse_args()
    cfg = load_yaml(args.cfg)
    args.root.mkdir(exist_ok=True)

    rng = np.random.RandomState(args.seed + 100 * rank)
    all_urdfs = find_urdfs(Path(cfg["urdf_root"]))
    origin = Transform.t_[0.0, 0.0, 0.05]

    sim = GraspSim(cfg["sim"], rng)
    grasp_sampler = UniformPointCloudSampler(sim.robot, rng)
    score_fn = get_metric(cfg["metric"], sim, cfg.get(cfg["metric"], {}))

    grasp_count = args.count // worker_count
    scene_count = grasp_count // cfg["scene_grasp_count"]

    for _ in tqdm(range(scene_count), disable=rank != 0):
        # Generate a new scene
        sim.scene.clear()
        object_count = rng.poisson(cfg["object_count_lambda"]) + 1
        urdfs = rng.choice(all_urdfs, object_count)
        scales = rng.uniform(cfg["scaling"]["low"], cfg["scaling"]["high"], len(urdfs))
        sim.robot.reset(Transform.t_[np.full(3, 100)], sim.robot.max_width)
        sim.scene.generate(origin, urdfs, scales)
        state_id = sim.save_state()

        # Sample camera views
        view_count = rng.randint(cfg["max_view_count"]) + 1
        views = sample_views(sim.scene, view_count, rng)

        # Render images
        imgs = render_imgs(views, sim.camera)

        # Reconstruct point cloud
        pc = create_pc(sim.scene, imgs, sim.camera.intrinsic, views)

        if pc.is_empty():
            continue

        # Sample grasps
        grasps = grasp_sampler(cfg["scene_grasp_count"], pc)

        # Evaluate grasps
        qualities = [evaluate_grasp_point(g, sim, state_id, score_fn) for g in grasps]

        # Write
        db.write(args.root, views, imgs, grasps, qualities)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cfg", type=Path, default="cfg/dataset/blocks.yaml")
    parser.add_argument("--count", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=1)
    return parser.parse_args()


def setup_mpi():
    worker_count = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()
    return worker_count, rank


def sample_views(scene, view_count, rng):
    views = []
    for _ in range(view_count):
        r = rng.uniform(1.6, 2.4) * scene.size
        theta = rng.uniform(0.0, np.pi / 4.0)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        views.append(view_on_sphere(scene.center, r, theta, phi))
    return views


def render_imgs(views, camera):
    return [camera.get_image(view)[1] for view in views]


def create_pc(scene, imgs, intrinsic, views):
    tsdf = create_tsdf(scene.size, 120, imgs, intrinsic, views)
    pc = tsdf.get_scene_cloud()
    lower = np.r_[0.02, 0.02, scene.center.translation[2] + 0.01]
    upper = np.r_[scene.size - 0.02, scene.size - 0.02, scene.size]
    bounding_box = o3d.geometry.AxisAlignedBoundingBox(lower, upper)
    return pc.crop(bounding_box)


def evaluate_grasp_point(grasp, sim, state_id, quality_fn, rot_count=6):
    # Changes the rotation of the grasp in place
    angles = np.linspace(0.0, np.pi, rot_count)
    R = grasp.pose.rotation
    for angle in angles:
        grasp.pose.rotation = R * Rotation.from_rotvec([0, 0, angle])
        sim.restore_state(state_id)
        quality, _ = quality_fn(grasp)
        if quality:
            return 1.0
    return 0.0


if __name__ == "__main__":
    main()
