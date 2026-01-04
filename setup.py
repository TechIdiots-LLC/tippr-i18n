#!/usr/bin/env python3
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='tippr_i18n',
    version="0.1.0",
    install_requires=["r2"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'tippr_i18n': ['i18n/*/LC_MESSAGES/*.mo']},
    python_requires='>=3.8',
    entry_points="""
    [paste.app_factory]
    main = tippr_i18n.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
