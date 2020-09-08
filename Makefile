.PHONY: build-lib upload 

build-lib: dist/

upload: .stamps/upload

dist/: $(shell find aida examples -type f) README.md requirements.txt pyproject.toml
	poetry build

.stamps/upload: dist/
	poetry publish
	mkdir -p .stamps && touch .stamps/upload
