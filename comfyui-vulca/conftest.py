# Prevent pytest from treating this directory as a package.
# Tests import `nodes` directly via sys.path manipulation in test_nodes.py.
collect_ignore = ["__init__.py"]
