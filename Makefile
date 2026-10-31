PYTHON ?= python3
SCOPE ?= full

.PHONY: test scope verify install-plan install-local verify-docs verify-scripts verify-unit

test:
	"$(PYTHON)" scripts/harness.py verify --scope full

scope:
	"$(PYTHON)" scripts/harness.py scope

verify:
	"$(PYTHON)" scripts/harness.py verify --scope "$(SCOPE)"

install-plan:
	"$(PYTHON)" scripts/harness.py install

install-local:
	"$(PYTHON)" scripts/harness.py install --apply

verify-docs:
	"$(PYTHON)" scripts/verify_repo.py --root .

verify-scripts:
	git diff --check
	git diff --cached --check
	"$(PYTHON)" scripts/verify_repo.py --root . --scripts-only

verify-unit:
	"$(PYTHON)" -m unittest discover -s tests -p 'test_*.py' -v
