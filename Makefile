PYTHON = python
GIT = git


clean:
	@find . -name \*.py[co] -delete
	@find . -type d -name "__pycache__" -delete


version: clean
	@$(PYTHON) -c "from auxlib.packaging import get_version; print get_version('auxlib')"



release: clean
	VERSION = $(shell make version)
	$(ECHO) $(VERSION) > .version
	$(GIT) add .version
	#$(GIT) commit -m "release $(VERSION)"
	#$(GIT) push
	#$(GIT) tag "$(VERSION)"
	#$(GIT) push --tags
	#$(PYTHON) setup.py release


.PHONY: clean release version
