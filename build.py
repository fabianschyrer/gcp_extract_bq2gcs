from __future__ import absolute_import
import os, sys
import subprocess

from pybuilder.core import init, use_plugin, task

sys.path.append(os.getcwd())

use_plugin("python.core")
use_plugin("python.distutils")
use_plugin("python.unittest")
use_plugin('python.pycharm')
use_plugin("python.coverage")
use_plugin("python.install_dependencies")

default_task = ['remove_pyc', 'publish', 'copy_requirements']


@init
def initialize(project):
    project.build_depends_on('mockito')
    project.set_property("dir_dist_scripts", 'scripts')
    project.set_property('dir_source_unittest_python', os.path.join('src', 'tests', 'python'))
    project.set_property('coverage_threshold_warn', 0)
    project.include_file('sftp', 'sftp/profiles/*/*.yaml')

    project.set_property('coverage_exceptions', 'main.py')

@task
def remove_pyc():
    dist_path = os.path.join('target', 'dist')
    for path, dir, files in os.walk(dist_path):
        for file_name in files:
            if file_name.endswith('.pyc'):
                os.remove(os.path.join(path, file_name))

@task
def copy_requirements():
    subprocess.call('cp requirements.txt {}'.format(os.path.join('target', 'dist', '*')), shell=True)
