.PHONY: build-lib upload-testing upload

.stamps/:
	mkdir .stamps

.stamps/lib: .stamps/ aida/* README.md requirements.txt setup.py
	rm -r build/ dist/ | /bin/true
	python setup.py bdist_wheel
	twine check dist/*
	touch .stamps/lib

build-lib: .stamps/lib

upload-testing: .stamps/lib
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload: .stamps/lib
	twine upload dist/*