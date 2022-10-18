import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

test_requires = [
    "django-constance",
    "redis",
    "pytest",
    "pytest-coverage",
    "pytest-django",
    "pytest-mock",
    "credstash>=1.0.0,<2",
]

TOX_ENV = os.environ.get("TOX_ENV_NAME", "django22")  # Added in tox 3.4
if "django20" in TOX_ENV:
    test_requires.append("Django>=2.0,<2.1")
elif "django21" in TOX_ENV:
    test_requires.append("Django>=2.1,<2.2")
elif "django30" in TOX_ENV:
    test_requires.append("Django>=3.0,<3.1")
elif "django31" in TOX_ENV:
    test_requires.append("Django>=3.1,<3.2")
elif "django32" in TOX_ENV:
    test_requires.append("Django>=3.2,<3.3")
elif "django40" in TOX_ENV:
    test_requires.append("Django>=4.0,<4.1")
elif "django41" in TOX_ENV:
    test_requires.append("Django>=4.1,<4.2")
else:
    # Default to the regular requirements
    test_requires.append("Django>=2.2,<5")

setup(
    name="configular",
    packages=["configular"],
    include_package_data=True,
    description="Support hierarchical loading of applications settings from a number of sources.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Aaron McMillin",
    author_email="amcmillin@jbssolutions.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Installation/Setup",
        "Framework :: Django",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    extras_require={
        "constance": ["django-constance>=2.0.0,<3"],
        "credstash": ["credstash>=1.0.0,<2"],
        "django": ["Django>=2.2,<4"],
        "test": test_requires,
    },
    use_scm_version={
        # PyPi doesn't allow local versions
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
)
