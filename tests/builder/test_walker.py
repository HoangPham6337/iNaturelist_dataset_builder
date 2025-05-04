from pathlib import Path
from dataset_builder.builder.walker import build_copy_tasks  # type: ignore


def test_build_copy_tasks_empty():
    tasks = list(build_copy_tasks({}, ["Aves"], Path("src"), Path("dst")))
    assert tasks == []


def test_build_copy_tasks_filters_targets(tmp_path: Path):
    matched = {"Aves": ["sparrow"], "Insecta": ["ant"]}
    src_root = Path("src_root")
    dst_root = Path("dst_root")
    tasks = list(build_copy_tasks(matched, ["Aves"], src_root, dst_root))
    assert len(tasks) == 1
    cls, sp, src, dst = tasks[0]
    assert cls == "Aves"
    assert sp == "sparrow"
    assert src == src_root / "Aves" / "sparrow"
    assert dst == dst_root / "Aves" / "sparrow"