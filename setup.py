from setuptools import setup

setup(name='weta_importer',
      version='1.0',
      packages=['weta_datastore'],
      entry_points={
              'console_scripts': ['weta-import=weta_datastore.weta_importer:main'],
          },
      )
