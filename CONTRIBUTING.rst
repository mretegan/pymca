Contributing
============

Developer Installation
-----------------------

Perform an editable install with all requirements

.. code:: bash

    pip install -r requirements.txt -e .

Start the main application

.. code:: bash

    pymca

or using the module directly

.. code:: bash

    python -m PyMca5.PyMcaGui.pymca.PyMcaMain

Release
-------

Main Steps
##########

1) Update version in ``src/PyMca5/__init__.py``
2) Wait until release action is finished
3) Download and `test` Windows and macOS frozen binaries
4) Update ``changelog.txt``

Start
#####

Start the release procedure by pushing a commit to the `master` branch with modified version in `src/PyMca5/__init__.py`. The release pipeline is not triggered by PRs. If the release pipeline fails during the `wheels` step before the upload to TestPyPI, changes can be committed and the release pipeline can be triggered manually. The release includes uploading wheels to TestPyPI and PyPI, as well as creating executable files (installer for Windows and universal DMG for macOS).

The entire release pipeline can take about an hour.

If you need to make complicated modifications to the CI workflow, please create a fork and run all your CI in the fork.

Test
####

The CI runs tests on wheels and tries to run tests in the GUI. To be sure that there are no bugs, the tests should be run directly in frozen binaries manually using the following procedure:

`call/load 1D plugins` → `interactive console`

.. image:: package/NavigationImages/InteractiveConsole.png
   :alt: interactive_console

.. code:: bash

   from PyMca5.tests import TestAll
   TestAll.main()

Few tests will be skipped, and none should fail.

Please note that tests should be performed on Windows, macOS-arm64 and macOS-x86.

Changelog
#########

A list of pull requests will be generated in the release comments but not in ``changelog.txt``, which should be updated manually, since not all pull requests are described clearly when created.

Availability
############
New versions of PyMca5 will be distributed via GitHub releases.

Older versions (<5.9.5) are available at https://sourceforge.net/projects/pymca/files/pymca/PyMca5.9.4/


