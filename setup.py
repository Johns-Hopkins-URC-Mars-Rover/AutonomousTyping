from setuptools import find_packages, setup

package_name = 'autonomous_typing'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='joshuadayal',
    maintainer_email='joshuadayal72@gmail.com',
    description='Autonomous typing package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # format: 'executable_name = package_name.python_file_name:main_function'
            'movement_vector_publisher = autonomous_typing.movement_vector_publisher:main',
            'movement_vector_subscriber = autonomous_typing.movement_vector_subscriber:main',
        ],
    },
)
