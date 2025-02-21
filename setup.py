from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()
    
with open('README_pypi.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pybimscantools',
    version='0.1.0.post2',
    packages=find_packages(),  # Automatically find and include all packages (i.e., directories with __init__.py)
    include_package_data=True,  # Include non-Python files (e.g., ifcconvert.exe)
    package_data={
        'pybimscantools': ['IfcConvert.exe'],  # Include the .exe file in the 'pybimscantools' package
    },
    install_requires=required,
    description='A python packages for automated data acquisition pipeline for HumanTech project',
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for Markdown
    author='Michael Peter, Patipol Thanuphol',
    author_email='pmic@zhaw.ch, thau@zhaw.ch, patipol.thanu@gmail.com',
    url='https://github.com/Patipolt/pybimscantools.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',  # Specify the minimum Python version your package requires
)