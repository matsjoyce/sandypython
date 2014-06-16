coverage run --branch do_tests.py
coverage html --omit='sandypython/safe_dill/dill.py,sandypython/safe_dill/pickle.py,tests/*,doc/*'
coverage erase
pep8 .
