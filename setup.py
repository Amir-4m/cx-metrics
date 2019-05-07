#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from setuptools import setup, find_packages
import os
import cx_metrics

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Programming Language :: Python :: 3.5',
]

requirements_path = os.path.join(os.path.dirname(__file__), 'requirements', 'base.txt')
with open(requirements_path, 'r') as f:
    requirements = f.read().split('\n')

requirements.append('django-fancy-imagefield')
requirements.append('django-contrib')
requirements.append('upkook-core')
requirements.append('django>=2.1,<2.3')
INSTALL_REQUIREMENTS = requirements

readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(readme_path).read()

setup(
    name="cx_metrics",
    version=cx_metrics.__version__,
    description="Django contrib apps",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/upkook/cx-metrics',
    author=cx_metrics.__author__,
    author_email="saeed@upkook.com",
    python_requires=">=3.5",
    packages=find_packages(exclude=[]),
    install_requires=INSTALL_REQUIREMENTS,
    extras_require={},
    test_suite='run_tests.main',
    platforms=['OS Independent'],
    include_package_data=True,
    zip_safe=False,
    classifiers=CLASSIFIERS,
    dependency_links=[
        'git+ssh://git@github.com/nargeel/django-fancy-imagefield.git@master#egg=django-fancy-imagefield',
        'git+ssh://git@github.com/nargeel/django-contrib.git@master#egg=django-contrib',
        'git+ssh://git@bitbucket.org/upkook/upkook-core.git@develop#egg=upkook-core'
    ]
)
