VERSION = $(shell cat auxlib/.version)


clean:
	find . -name \*.py[co] -delete
	find . -type d -name "__pycache__" -delete
	rm -rf *.egg* .eggs .tox dist


release: clean
	@echo "version=$(VERSION)"
	@git add --all
	@git commit -m "release $(VERSION)"
	@git tag "$(VERSION)"
	git push && git push --tags
	python setup.py release


.PHONY: clean release version
