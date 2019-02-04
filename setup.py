from setuptools import setup, find_packages

setup(name='weta_datastore',
      version='0.1',
      author='Fan Wang',
      author_email='fanwangg@gmail.com',
      packages=find_packages(),
      entry_points={
              'console_scripts': ['weta_import=weta_datastore.weta_import:main',
                                  'weta_query=weta_datastore.weta_query:main'],
          },
      )
