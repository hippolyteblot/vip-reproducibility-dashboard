from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'girder>=3.0.0a1',
    'pandas',
    'docker',
    'bson',
    'girder'
]

setup(
    author='Hippolyte Blot',
    author_email='	hippolyte.blot@creatis.insa-lyon.fr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    description='Automatically convert quest2 files to feather for the VIP reproducibility dashboard',
    install_requires=requirements,
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='girder-plugin, auto_feather',
    name='auto_feather',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/girder/auto_feather',
    version='0.1.0',
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'auto_feather = auto_feather:GirderPlugin'
        ]
    }
)
