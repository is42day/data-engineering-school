from pathlib import Path


def test_expected_learning_directories_exist() -> None:
    expected = [
        Path("src/de_school"),
        Path("sql"),
        Path("docs"),
        Path("data/source"),
    ]

    missing = [str(path) for path in expected if not path.exists()]
    assert not missing, f"Missing expected project paths: {missing}"


def test_pipeline_exposes_run_function() -> None:
    from de_school.pipeline import run

    assert callable(run)
