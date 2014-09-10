all:
	python -m noteorganiser/NoteOrganiser

test:
	py.test noteorganiser/ -v --doctest-modules
