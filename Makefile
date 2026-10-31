PYTHON ?= python3

.PHONY: test verify-docs verify-scripts verify-unit

test: verify-docs verify-scripts verify-unit

verify-docs:
	$(PYTHON) scripts/verify_repo.py --root .

verify-scripts:
	git diff --check
	$(PYTHON) scripts/verify_repo.py --root . --scripts-only

verify-unit:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
