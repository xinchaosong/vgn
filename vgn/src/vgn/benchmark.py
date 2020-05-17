from datetime import datetime
from pathlib2 import Path


import numpy as np
import pandas
from pandas import DataFrame


class Logger(object):
    def __init__(self, log_dir, descr):
        descr = "{} {}".format(datetime.now().strftime("%y%m%d-%H%M%S"), descr)
        root = Path(log_dir) / descr
        root.mkdir(exist_ok=True)

        self.rounds_csv_path = root / "rounds.csv"
        if not self.rounds_csv_path.exists():
            DataFrame(columns=["round_id", "object_count"]).to_csv(
                self.rounds_csv_path, index=False
            )

        self.trials_csv_path = root / "trials.csv"
        if not self.trials_csv_path.exists():
            DataFrame(columns=["round_id", "planning_time", "score", "label"]).to_csv(
                self.trials_csv_path, index=False
            )

    def add_round(self, round_id, object_count):
        rounds = pandas.read_csv(self.rounds_csv_path)
        rounds.append(
            {"round_id": round_id, "object_count": object_count,}, ignore_index=True,
        ).to_csv(self.rounds_csv_path, index=False)

    def log_trial(self, round_id, planning_time, score, label):
        trials = pandas.read_csv(self.trials_csv_path)
        trials.append(
            {
                "round_id": round_id,
                "planning_time": planning_time,
                "score": score,
                "label": label,
            },
            ignore_index=True,
        ).to_csv(self.trials_csv_path, index=False)

    @property
    def success_rate(self):
        pass

    @property
    def percent_cleared(self):
        pass

    @property
    def planning_time(self):
        pass
