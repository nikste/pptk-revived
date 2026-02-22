"""
Build and packaging tests for pptk-revived.

Layer 1 — fast (no marker): metadata and pyproject.toml consistency.
          Works after a clean clone with `pip install -e .` (no cmake needed).
          Requires Python 3.11+ (uses tomllib).

Layer 2 — slow (@pytest.mark.build): cmake → uv build → install → import.
          Requires system deps: cmake, Qt5, TBB, Eigen, patchelf, uv on PATH.

Run layer 2 with:
    pytest -m build tests/test_build.py -v
"""
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="requires Python 3.11+ for tomllib",
)

# ── Layer 1: fast metadata tests ──────────────────────────────────────────────

def test_pyproject_has_name():
    import tomllib
    data = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    assert data['project']['name'] == 'pptk-revived'


def test_pyproject_has_version():
    import tomllib
    data = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    assert data['project']['version']


def test_pyproject_version_matches_pptk():
    import tomllib
    import pptk
    data = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    assert pptk.__version__ == data['project']['version']


def test_pyproject_numpy_in_build_requires():
    """numpy must be in build-system requires so cmake finds it in uv's isolated env."""
    import tomllib
    data = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    requires = data['build-system']['requires']
    assert any('numpy' in r for r in requires), \
        "numpy missing from [build-system] requires"


def test_pyproject_requires_python():
    import tomllib
    data = tomllib.loads((ROOT / 'pyproject.toml').read_text())
    assert '3.9' in data['project']['requires-python']


def test_pptk_revived_reexports():
    """pptk_revived must expose the same viewer and estimate_normals as pptk."""
    import pptk
    import pptk_revived
    assert pptk_revived.viewer is pptk.viewer
    assert pptk_revived.estimate_normals is pptk.estimate_normals
    assert pptk_revived.__version__ == pptk.__version__


# ── Layer 2: end-to-end build tests ──────────────────────────────────────────

def _artifacts_present():
    """Return True if all pre-compiled artifacts exist in the source tree."""
    import platform
    ext = '.so' if platform.system() != 'Windows' else '.pyd'
    exe = '' if platform.system() != 'Windows' else '.exe'
    return all([
        (ROOT / 'pptk' / 'kdtree' / f'kdtree{ext}').exists(),
        (ROOT / 'pptk' / 'processing' / 'estimate_normals' / f'estimate_normals{ext}').exists(),
        (ROOT / 'pptk' / 'vfuncs' / f'vfuncs{ext}').exists(),
        (ROOT / 'pptk' / 'viewer' / f'viewer{exe}').exists(),
    ])


@pytest.mark.build
def test_cmake_build(tmp_path):
    """Compile C++ extensions with cmake and copy artifacts into the source tree.

    Builds into ROOT/_cmake_build/ (not tmp_path) so that the compiled .so
    files land in the source tree.  This lets subsequent uv build calls find
    the artifacts via MANIFEST.in and skip cmake entirely — keeping the test
    suite fast (cmake runs only once per session).
    """
    import platform
    import shutil

    if _artifacts_present():
        pytest.skip("Pre-compiled artifacts already present; skipping cmake step.")

    build_dir = ROOT / '_cmake_build'
    build_dir.mkdir(exist_ok=True)
    subprocess.run(
        ['cmake', str(ROOT), '-DCMAKE_BUILD_TYPE=Release',
         f'-DPython3_EXECUTABLE={sys.executable}'],
        cwd=build_dir, check=True,
    )
    subprocess.run(
        ['cmake', '--build', str(build_dir), '--', '-j4'],
        check=True,
    )

    # Copy artifacts into source tree so subsequent uv build calls skip cmake.
    ext = '.so' if platform.system() != 'Windows' else '.pyd'
    exe = '' if platform.system() != 'Windows' else '.exe'
    cmake_pptk = build_dir / 'pptk'
    for subdir, fname in [
        (Path('kdtree'), f'kdtree{ext}'),
        (Path('processing') / 'estimate_normals', f'estimate_normals{ext}'),
        (Path('vfuncs'), f'vfuncs{ext}'),
        (Path('viewer'), f'viewer{exe}'),
    ]:
        src = cmake_pptk / subdir / fname
        dst = ROOT / 'pptk' / subdir / fname
        assert src.exists(), f"Expected cmake artifact not found: {src}"
        shutil.copy2(src, dst)

    src_libs = cmake_pptk / 'libs'
    if src_libs.is_dir():
        shutil.copytree(src_libs, ROOT / 'pptk' / 'libs', dirs_exist_ok=True)

    assert _artifacts_present(), "cmake ran but artifacts still missing in source tree"


@pytest.mark.build
def test_uv_build_succeeds(tmp_path):
    """uv build produces a wheel and an sdist."""
    result = subprocess.run(
        ['uv', 'build', '--out-dir', str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        f"uv build failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert list(tmp_path.glob('*.whl')), "No wheel produced"
    assert list(tmp_path.glob('*.tar.gz')), "No sdist produced"


@pytest.mark.build
def test_uv_build_skips_cmake(tmp_path):
    """When .so files are present, uv build must not invoke cmake."""
    if not _artifacts_present():
        pytest.skip(
            "Pre-compiled artifacts not in source tree; "
            "run test_cmake_build first to populate them."
        )
    result = subprocess.run(
        ['uv', 'build', '--out-dir', str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    # uv captures build-backend stdout into its own stderr
    combined = result.stdout + result.stderr
    assert 'Pre-compiled artifacts found; skipping cmake build.' in combined, \
        f"Skip message not found.\nstdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.build
def test_wheel_installs_and_imports(tmp_path):
    """Install built wheel into a fresh uv venv; verify pptk and pptk_revived import."""
    result = subprocess.run(
        ['uv', 'build', '--out-dir', str(tmp_path), '--python', sys.executable],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    wheel = next(tmp_path.glob('*.whl'))

    venv = tmp_path / 'venv'
    subprocess.run(
        ['uv', 'venv', str(venv), '--python', sys.executable],
        check=True, capture_output=True,
    )
    python = venv / 'bin' / 'python'

    subprocess.run(
        ['uv', 'pip', 'install', str(wheel), '--python', str(python)],
        check=True, capture_output=True,
    )

    out = subprocess.run(
        [str(python), '-c',
         'import pptk, pptk_revived\n'
         'assert pptk.__version__ == pptk_revived.__version__\n'
         'assert pptk_revived.viewer is pptk.viewer\n'
         'print("OK", pptk.__version__)'],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, f"Import check failed:\n{out.stdout}\n{out.stderr}"
    assert out.stdout.strip().startswith('OK')


@pytest.mark.build
def test_wheel_contains_required_files(tmp_path):
    """Wheel must contain pptk/, pptk_revived/, compiled extensions, and viewer."""
    subprocess.run(
        ['uv', 'build', '--out-dir', str(tmp_path), '--wheel'],
        cwd=ROOT, check=True, capture_output=True,
    )
    wheel = next(tmp_path.glob('*.whl'))
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
    assert any('pptk/' in n for n in names)
    assert any('pptk_revived/' in n for n in names)
    assert any('kdtree' in n for n in names)
    assert any('estimate_normals' in n for n in names)
    assert any('vfuncs' in n for n in names)
    assert any('viewer' in n and 'viewer.py' not in n for n in names)
