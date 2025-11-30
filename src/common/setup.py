from setuptools import setup
import os
from glob import glob

package_name = 'common'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'networkx', 'numpy', 'pyyaml'],
    zip_safe=True,
    maintainer='User',
    maintainer_email='user@example.com',
    description='Common utilities and graph structures',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'metrics_node = common.metrics_node:main',
        ],
    },
)

