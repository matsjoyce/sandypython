coverage run -p do_tests.py
coverage run -p sandbox/spec.py
coverage combine
coverage html --omit=safe_dill/dill.py,safe_dill/pickle.py
coverage erase