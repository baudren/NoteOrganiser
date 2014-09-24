all:
	python -m noteorganiser/NoteOrganiser

test:
	py.test --cov noteorganiser noteorganiser/ -v --doctest-modules
