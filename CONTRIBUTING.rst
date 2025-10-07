Contributing
============

Developers installation
-----------------------

Editable install with all requirements

.. code:: bash

    pip install -r requirements.txt -e .

Start the main application

.. code:: bash

    pymca

or using the module directly

.. code:: bash

    python -m PyMca5.PyMcaGui.pymca.PyMcaMain

Release
----------
Main steps
#######

1) Push new version into ``src/PyMca5/__ini__.py``
2) Wait until release action is finished
3) Download and `test` Windwos and MacOS frozen binaries
4) Update ``changelog.txt``

Start
#######

To start release procedure one need to push commit with modified version in src/PyMca5/__ini__.py. If release procedure was broken on `wheels` step before uploading to test-PyPI, one can push changes and restart release manually.
The release include upload wheels to test-PyPI and PyPI as well as creating executable files (installer for Windows and universal dmg for MacOS).

The action can take about an hour.

Test
#######

The CI run tests using wheels and only check that bundled versions do not crush on launch to avoid any incompatibility. That is why frozen (fat) binaries should be tested manually! using the following procedure:

`call/load 1D plugins` → `interactive console`

.. image:: NavigationImages/InteractiveConsole.png
   :alt: interactive_console

.. code:: bash

   from PyMca5.tests import TestAll
   TestAll.main()

Few tests will be skipped, and none should fail.

Please notice that tests `should` be performed on Windows, MacOS-arm64 and MacOS-x86.

Changelog
#########

List of pull request will be generated in the release comments but not in ``changelog.txt``, which should be updated manually, since not all pull requests are described clearly when created.

Availability
############
New versions of PyMca5 will be distributed via github releases.

Older version (<5.9.5) are available at https://sourceforge.net/projects/pymca/files/pymca/PyMca5.9.4/


