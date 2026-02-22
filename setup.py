from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import os
import os.path
import shutil
import platform

from packaging.tags import sys_tags

_tag = next(iter(sys_tags()))
wheel_tags = (_tag.interpreter, _tag.abi, _tag.platform)

system_type = platform.system()

license_text = b''
with open('LICENSE', 'rb') as fd:
    license_text = license_text + fd.read()
license_append_candidates = [
    os.path.join('licenses', 'LICENSE.append.txt'),
    os.path.join('licenses', 'LICENSE.append.linux.txt'),
    os.path.join('licenses', 'LICENSE.append.macos.txt'),
    os.path.join('licenses', 'LICENSE.append.windows.txt'),
]
for _candidate in license_append_candidates:
    if os.path.isfile(_candidate):
        with open(_candidate, 'rb') as fd:
            license_text = license_text + fd.read()
        break
with open(os.path.join('pptk', 'LICENSE'), 'wb') as fd:
    fd.write(license_text)

def make_mod(x):
    if system_type == 'Windows':
        return x + '.pyd'
    elif system_type == 'Linux':
        return x + '.so'
    elif system_type == 'Darwin':
        return x + '.so'
    else:
        raise RuntimeError('Unknown system type %s', system_type)


def make_lib(x, version_suffix=''):
    if system_type == 'Windows':
        return x + '.dll'
    elif system_type == 'Linux':
        return 'lib' + x + '.so' + version_suffix
    elif system_type == 'Darwin':
        return 'lib' + x + '.dylib'
    else:
        raise RuntimeError('Unknown system type %s', system_type)


def make_exe(x):
    if system_type == 'Windows':
        return x + '.exe'
    else:
        return x


class CMakeBuild(build_ext):
    """Run cmake + make to compile C++ extensions before packaging."""

    def run(self):
        src_dir = os.path.dirname(os.path.abspath(__file__))

        # If all pre-compiled artifacts already exist (e.g. when installing
        # from a pre-built sdist or editable install), skip the cmake step.
        artifacts = [
            os.path.join(src_dir, 'pptk', 'kdtree', make_mod('kdtree')),
            os.path.join(src_dir, 'pptk', 'processing', 'estimate_normals',
                         make_mod('estimate_normals')),
            os.path.join(src_dir, 'pptk', 'vfuncs', make_mod('vfuncs')),
            os.path.join(src_dir, 'pptk', 'viewer', make_exe('viewer')),
        ]
        if all(os.path.exists(a) for a in artifacts):
            print('Pre-compiled artifacts found; skipping cmake build.')
            return

        build_dir = os.path.join(src_dir, '_cmake_build')
        os.makedirs(build_dir, exist_ok=True)

        # Configure — pass the active Python so cmake finds numpy in the venv
        import sys
        subprocess.check_call(
            ['cmake', src_dir,
             '-DCMAKE_BUILD_TYPE=Release',
             f'-DPython3_EXECUTABLE={sys.executable}'],
            cwd=build_dir)

        # Build (use all available cores)
        import multiprocessing
        jobs = str(multiprocessing.cpu_count())
        subprocess.check_call(
            ['cmake', '--build', build_dir, '--', '-j', jobs],
            cwd=build_dir)

        # Copy compiled artifacts from _cmake_build/pptk/ back into source tree
        cmake_pptk = os.path.join(build_dir, 'pptk')
        _copy_artifact(cmake_pptk, 'kdtree', make_mod('kdtree'), src_dir)
        _copy_artifact(cmake_pptk, os.path.join('processing', 'estimate_normals'),
                       make_mod('estimate_normals'), src_dir)
        _copy_artifact(cmake_pptk, 'vfuncs', make_mod('vfuncs'), src_dir)
        _copy_artifact(cmake_pptk, 'viewer', make_exe('viewer'), src_dir)

        # Copy Qt libs (flat files only — subdirs are handled separately)
        src_libs = os.path.join(cmake_pptk, 'libs')
        dst_libs = os.path.join(src_dir, 'pptk', 'libs')
        if os.path.isdir(src_libs):
            shutil.copytree(src_libs, dst_libs, dirs_exist_ok=True)

        # build_py runs before build_ext and collects package_data before the
        # .so files exist.  Copy artifacts directly into build_lib so the wheel
        # assembler finds them regardless of file-collection order.
        if self.build_lib:
            for subdir, fname in [
                ('kdtree', make_mod('kdtree')),
                (os.path.join('processing', 'estimate_normals'),
                 make_mod('estimate_normals')),
                ('vfuncs', make_mod('vfuncs')),
                ('viewer', make_exe('viewer')),
            ]:
                artifact = os.path.join(src_dir, 'pptk', subdir, fname)
                dst_dir = os.path.join(self.build_lib, 'pptk', subdir)
                if os.path.exists(artifact):
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.copy2(artifact, os.path.join(dst_dir, fname))
                else:
                    print(f'WARNING: artifact not found for wheel: {artifact}')
            bl_libs = os.path.join(self.build_lib, 'pptk', 'libs')
            if os.path.isdir(dst_libs):
                shutil.copytree(dst_libs, bl_libs, dirs_exist_ok=True)

    def build_extension(self, ext):
        pass  # all building is done in run()


def _copy_artifact(cmake_pptk, subdir, filename, src_dir):
    """Copy a single compiled artifact from the cmake build tree to the source tree."""
    src = os.path.join(cmake_pptk, subdir, filename)
    dst_dir = os.path.join(src_dir, 'pptk', subdir)
    dst = os.path.join(dst_dir, filename)
    if os.path.exists(src):
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        print(f'WARNING: expected cmake artifact not found: {src}')


def list_libs():
    libs_dir = os.path.join('pptk', 'libs')
    exclude_list = ['Makefile', 'cmake_install.cmake']
    return [f for f in os.listdir(libs_dir)
            if os.path.isfile(os.path.join(libs_dir, f))
            and f not in exclude_list]


setup(
    name='pptk-revived',
    version='0.1.1',
    description='A Python package for facilitating point cloud processing.',
    author='Nikolaas Steenbergen',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License'],
    license='MIT',
    install_requires=['numpy'],
    project_urls={
        'Source': 'https://github.com/nikste/pptk_revived'},
    ext_modules=[Extension('pptk._cmake', sources=[])],
    cmdclass={'build_ext': CMakeBuild},
    packages=find_packages(),
    package_data={
        'pptk': [
            os.path.join('libs', f) for f in list_libs()] + [
            'LICENSE',
            os.path.join('libs',
                         'qt_plugins', 'platforms', make_lib('*', '*')),
            os.path.join('libs',
                         'qt_plugins', 'xcbglintegrations', make_lib('*', '*'))
            ],
        'pptk.kdtree': [make_mod('kdtree')],
        'pptk.processing.estimate_normals': [make_mod('estimate_normals')],
        'pptk.vfuncs': [make_mod('vfuncs')],
        'pptk.viewer': [make_exe('viewer'), 'qt.conf']},
    options={'bdist_wheel': {
        'python_tag': wheel_tags[0],
        'plat_name': wheel_tags[2]}})
