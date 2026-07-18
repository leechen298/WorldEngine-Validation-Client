.PHONY: test-checker test-godot run-mvp

test-checker:
	@uv run --project checkers/mvp pytest -q checkers/mvp/tests

test-godot:
	@godot --headless --path executors/godot --script res://tests/test_contract.gd

run-mvp:
	@python3 scripts/run_mvp.py
