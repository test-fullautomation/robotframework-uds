.. Copyright 2020-2026 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

RobotFramework_UDS Package Description
======================================

Getting Started
---------------

The library **RobotFramework_UDS** provides a set of Robot Framework keywords 
for sending UDS (UnifiedDiagnostic Services) requests and interpreting responses 
from automotive electronic control units (ECUs).

Whether you’re testing diagnostic sessions, reading data, or controlling 
routines on an ECU, the UDS Library simplifies these tasks by offering specific 
keywords for almost any UDS service as defined in 
`ISO 14229 <https://automotive.wiki/index.php/ISO_14229>`_. 

These keywords are designed to handle the complexity of UDS communication, 
enabling you to write efficient and reliable automated tests.

How to install
--------------

The **RobotFramework-UDS** can be installed in two different ways.

1. Installation via PyPi (recommended for users)

   .. code::

      pip install RobotFramework-UDS

   `RobotFramework-UDS in PyPi <https://pypi.org/project/RobotFramework-UDS/>`_

2. Installation via GitHub (recommended for developers)

   * Clone the **robotframework-uds** repository to your machine.

     .. code::

        git clone https://github.com/test-fullautomation/robotframework-uds.git

     `RobotFramework-UDS in GitHub <https://github.com/test-fullautomation/robotframework-uds>`_

   * Use the following command to install **RobotFramework-UDS** (executed in repository main folder):

     .. code::

        python -m pip install .

     Or:

     .. code::

        python -m pip install --proxy <proxy> .

     This command will also download and install all dependencies that are required to work with the source files in the current repository.
     After the initial installation of **RobotFramework-UDS** is done, you have the following two possibilities:

     1. *Clean the previous installation*:

        .. code::

           python "./cleanup_installation.py"

        ``cleanup_installation.py`` explicitly deletes all files and folders within the component installation folder under
        ``site-packages`` and also deletes local build artefacts.

     2. *Render the component documentation*:

        .. code::

           python "./genpackagedoc.py"

        This would e.g. be required in case of changes in the interface of **RobotFramework-UDS**.

        The documentation is rendered by a separate application called **GenPackageDoc**, that is part
        of the build dependencies and runtime dependencies of **RobotFramework-UDS**.

        **GenPackageDoc** needs to be configured. Details about how to do this, can be found in the
        `README.rst <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/README.rst>`_
        (sections *Install dependencies* and *Configure dependencies*).

   * Use the following command to build **RobotFramework-UDS** (executed in repository main folder):

     .. code::

        python -m build .

     Or:

     .. code::

        python -m pip config set global.proxy <proxy>
        python -m build .


Package Documentation
---------------------

A detailed documentation of the RobotFramework_UDS package can be found here: `RobotFramework_UDS.pdf <https://github.com/test-fullautomation/robotframework-uds/blob/develop/RobotFramework_UDS/RobotFramework_UDS.pdf>`_

Feedback
--------

To give us a feedback, you can send an email to `Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

In case you want to report a bug or request any interesting feature, please don't
hesitate to raise a ticket.

Maintainers
-----------

`Thomas Pollerspöck <mailto:Thomas.Pollerspoeck@de.bosch.com>`_

`Mai Minh Tri <mailto:tri.maiminh@vn.bosch.com>`_

Contributors
------------

`Holger Queckenstedt <mailto:holger.queckenstedt@de.bosch.com>`_

`Tran Duy Ngoan <mailto:ngoan.tranduy@vn.bosch.com>`_

License
-------

Copyright 2020-2026 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    |License: Apache v2|

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. |License: Apache v2| image:: https://img.shields.io/pypi/l/robotframework.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0.html

