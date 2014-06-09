coverage run -p --branch do_tests.py
coverage run -p --branch sandypython/spec.py
coverage combine
coverage html --omit='sandypython/safe_dill/dill.py,sandypython/safe_dill/pickle.py,tests/*,doc/*'
coverage erase
pep8 .
