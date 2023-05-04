How To - Start Your Development
======================================================================

Here is a simple pipeline for any contributors to follow.

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

