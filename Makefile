VERSION = $(shell cat auxlib/.version)


test:
	python setup.py test


test-ci:
	py.test --cov auxlib --cov-report xml --junitxml junit.xml tests


clean:
	@./scripts/clean


release: clean
	# @echo "version=$(VERSION)"
	# @git add --all
	# @git commit -m "release $(VERSION)"
	@git tag "$(VERSION)"
	git push && git push --tags
	python setup.py release


ve:
	@tox -e devenv
	@echo "\n\nnow run  $ source ve/bin/activate\n"


version:
	@echo $(VERSION)


.PHONY: clean release test ve version
