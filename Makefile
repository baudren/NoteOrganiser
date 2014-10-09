all:
	python -m noteorganiser/NoteOrganiser

3:
	python3 noteorganiser/NoteOrganiser.py

test-2:
	py.test-2.7 --cov noteorganiser noteorganiser/ -v --doctest-modules

test-3:
	py.test-3.3 --cov noteorganiser noteorganiser/ -v --doctest-modules

test: test-2 test-3

test-single:
	py.test --cov noteorganiser noteorganiser/ -v --doctest-modules

