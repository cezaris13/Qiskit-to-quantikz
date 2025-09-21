run:
	python qiskit_quantikz.py
test:
	python -m pytest -rP ./tests/*.py
build_package:
	python3 -m build
publish_package:
	python3 -m twine upload --repository testpypi dist/* --verbose
