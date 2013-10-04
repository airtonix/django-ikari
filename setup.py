from setuptools import setup, find_packages

import ikari as app

setup(name="django-ikari",
      version=app.__version__,
      description="Django middleware to allow user configurable domain anchoring to admin configured urlconfs.",
      author="Zenobius Jiricek",
      author_email="airtonix@gmail.com",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'django>=1.4',
          'django-appconf==0.4.1',
          'johnny-cache',
          'whois',
      ],
      tests_require=[
          'django-easytests',
      ]
      )
