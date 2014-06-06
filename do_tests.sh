coverage run -p --branch do_tests.py
coverage run -p --branch sandbox/spec.py
coverage combine
coverage html --omit='safe_dill/dill.py,safe_dill/pickle.py,tests/*'
coverage erase
pep8 .
