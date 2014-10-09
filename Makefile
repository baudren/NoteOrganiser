all:
	python -m noteorganiser/NoteOrganiser

test:
	py.test --cov noteorganiser noteorganiser/ -v --doctest-modules

3:
	python3 noteorganiser/NoteOrganiser.py

test3:
	py.test-3.3 --cov noteorganiser noteorganiser/ -v --doctest-modules

