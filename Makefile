.PHONY: build-lib upload-testing upload install-lib

install-lib: .stamps/local-install

build-lib: dist/

upload-testing: .stamps/upload-testing

upload: .stamps/upload

.stamps/:
	mkdir .stamps

dist/: $(shell find aida examples -type f) README.md requirements.txt setup.py
	rm -r build/ dist/ || /bin/true
	python setup.py bdist_wheel
	twine check dist/*

.stamps/upload-testing: .stamps/ dist/
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	touch .stamps/upload-testing

.stamps/upload: .stamps/ dist/
	twine upload dist/*
	touch .stamps/upload

.stamps/local-install: .stamps/ dist/
	activate aida-lib && python setup.py install
	touch .stamps/local-install