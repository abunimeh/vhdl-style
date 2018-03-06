"""A setuptools setup module for vhdllint."""

from cx_Freeze import setup, Executable

setup(
    name='vhdllint',
    version='0.1.0',
    description='Linter and style checker for VHDL',
    url='https://www.ohwr.org/projects/vhdl-style',
    author='Tristan Gingold - CERN BE-CO-HT',
    author_email='vhdl-style@ohwr.org',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)'

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='checker linter lint vhdl',
    packages=['vhdllint', 'vhdllint.filerules', 'vhdllint.lexrules',
              'vhdllint.semrules', 'vhdllint.syntaxrules',
              'vhdllint.synthrules'],
    install_requires=['libghdl'],
    executables=[Executable('ohwr.py',
                            targetName='vhdllint-ohwr.exe')]
)
