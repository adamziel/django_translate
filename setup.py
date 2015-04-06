from setuptools import setup, find_packages

setup(
    name="django_translate",
    version="1.0.0",
    author="Adam Zieliński",
    author_email="adam@sf2.guru",
    packages=find_packages(),
    include_package_data=True,
    url="http://pypi.python.org/pypi/django_translate_v100/",

    license="LICENSE",
    description="Non-gettext translations for django.",

    # Dependent packages (distributions)
    install_requires=[
        "python_translate"
    ],
)