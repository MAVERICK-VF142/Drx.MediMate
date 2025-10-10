import sys
import os
import pytest

# Get the path to the root of the project
project_root = os.path.dirname(os.path.abspath(__file__))

# Add the project root to the system path.
# This makes modules like 'backend' directly importable.
sys.path.insert(0, project_root)

# Now, run Pytest to discover and execute tests in the 'tests' directory.
# The ['tests', '-v'] arguments tell Pytest to look in the 'tests' folder
# and to run with verbose output.
pytest.main(['tests', '-v'])