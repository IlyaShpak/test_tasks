Install
------

    # clone the repository
    $ git clone https://github.com/IlyaShpak/test_tasks.git
    $ cd test_tasks/task_2
Edit connection params in __init__.py


Create a virtualenv and activate it::

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Or on Windows cmd::

    $ py -3 -m venv .venv
    $ .venv\Scripts\activate.bat

Install requirements::

    $ pip install -r requirements.txt


Install my_app::

    $ pip install -e .


Run
---

    $ flask --app my_app run

Use
---
    $ Open http://127.0.0.1:5000 in a browser.
    $ Create account
    $ Upload your data
    $ Test search
