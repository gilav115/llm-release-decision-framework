"""Filesystem artifact persistence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from time import gmtime, strftime

from rdf.models import ReleaseDecision, ScenarioRun


class FilesystemStorage:
    """Writes run artifacts in a stable, inspectable directory layout."""

    def create_run_dir(self, base_dir: str | Path) -> Path:
        """Create timestamped run directory under configured base path."""
        root = Path(base_dir)
        root.mkdir(parents=True, exist_ok=True)
        run_name = f"{strftime('%Y-%m-%dT%H-%M-%SZ', gmtime())}_run-001"
        run_dir = root / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def write_run_artifacts(
        self,
        run_dir: Path,
        run_config: dict,
        scenario_runs: list[ScenarioRun],
        release_decision: ReleaseDecision,
        summary_markdown: str,
    ) -> None:
        """Persist machine-readable and human-readable outputs for one run."""
        (run_dir / "run_config.json").write_text(json.dumps(run_config, indent=2))
        (run_dir / "scenario_runs.json").write_text(json.dumps([asdict(r) for r in scenario_runs], indent=2))
        (run_dir / "release_decision.json").write_text(json.dumps(asdict(release_decision), indent=2))
        (run_dir / "summary.md").write_text(summary_markdown)
        all_events = [asdict(e) for run in scenario_runs for e in run.system_events]
        (run_dir / "system_events.json").write_text(json.dumps(all_events, indent=2))
