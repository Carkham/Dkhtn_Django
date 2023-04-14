# Dkhtn_Django

BUAA-SE-2023-dkhtn's django repo

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Start With

    $ pip install -r requirements/local.txt

## Project Structure

```
dkhtn_django
│   README.md    
│   ...
└───dkhtn_django (apps)
│   │   logs (日志模块)
│   └───users (用户模块)
│       │   tests (单元测试)
│       │   urls.py
│       │   views.py
│       │   ...
│   
└───configs
    │   urls.py
    │   wsgi.py
    └───settings (配置文件)
```

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Type checks

Running type checks with mypy:

    $ mypy dkhtn_django

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.
