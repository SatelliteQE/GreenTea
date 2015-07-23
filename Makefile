all: verify

verify:
	find ./ -not -path "./env/*" -name "*.py" | xargs isort
	find ./ -not -path "./env/*" -name "*.py" | xargs autopep8 -i
