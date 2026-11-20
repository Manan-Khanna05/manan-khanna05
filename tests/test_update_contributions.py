import pathlib
import tempfile

import pytest

# Import the module under test
import scripts.update_contributions as uc


@pytest.fixture
def sample_data():
    """Return a minimal but realistic contribution data structure."""
    # 30 days of contributions with incremental counts
    contributions = [
        {"date": f"2024-01-{day:02d}", "count": day % 5}
        for day in range(1, 31)
    ]
    total = {"2023": 120, "2024": 80}
    return {"contributions": contributions, "total": total}


def test_build_svg_contains_expected_text(sample_data):
    """The generated SVG should contain key summary information."""
    svg = uc.build_svg(sample_data)

    # Verify that the SVG includes the total year, 30‑day sum and peak count
    total_year = sum(sample_data["total"].values())
    in30 = sum(c["count"] for c in sample_data["contributions"][-30:])
    peak = max(c["count"] for c in sample_data["contributions"][-30:])

    assert f"{total_year} Total Year" in svg
    assert f"{in30} in 30D" in svg
    assert f"Peak: {peak}/day" in svg

    # Basic sanity checks for SVG structure
    assert svg.strip().startswith("<svg")
    assert svg.strip().endswith("</svg>")


def test_svg_changed_detects_changes(tmp_path):
    """svg_changed should correctly detect when the SVG content differs."""
    # Create a temporary file to act as the existing SVG
    existing_file = tmp_path / "contributions.svg"
    existing_content = "<svg>old content</svg>"
    existing_file.write_text(existing_content, encoding="utf-8")

    # Monkey‑patch the module‑level SVG path to point at our temp file
    original_svg = uc.SVG
    uc.SVG = existing_file

    try:
        # Same content → no change
        assert not uc.svg_changed(existing_content)

        # Different content → change detected
        new_content = "<svg>new content</svg>"
        assert uc.svg_changed(new_content)
    finally:
        # Restore original constant to avoid side effects for other tests
        uc.SVG = original_svg
