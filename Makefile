.PHONY: build-lib upload-testing upload

build-lib: dist/

upload-testing: .stamps/upload-testing

upload: .stamps/upload

.stamps/:
	mkdir .stamps

dist/: $(shell find aida -type f) README.md requirements.txt setup.py
	rm -r build/ dist/ || /bin/true
	python setup.py bdist_wheel
	twine check dist/*

.stamps/upload-testing: .stamps/ dist/
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	touch .stamps/upload-testing

.stamps/upload: .stamps/ dist/
	twine upload dist/*
	touch .stamps/upload