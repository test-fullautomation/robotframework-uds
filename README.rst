.. Copyright 2020-2024 Robert Bosch GmbH

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

The **RobotFramework_UDS** can be installed in two different ways.

1. Installation via PyPi (recommended for users)

   .. code::

      pip install RobotFramework_UDS

   `RobotFramework_UDS in PyPi <https://pypi.org/project/RobotFramework_UDS/>`_

2. Installation via GitHub (recommended for developers)

   * Clone the **robotframework-uds** repository to your machine.

     .. code::

        git clone https://github.com/test-fullautomation/robotframework-uds.git

     `RobotFramework_UDS in GitHub <https://github.com/test-fullautomation/robotframework-uds>`_

   * Install dependencies

     **RobotFramework_UDS** requires some additional Python libraries. Before you install the cloned repository sources
     you have to install the dependencies manually. The names of all related packages you can find in the file ``requirements.txt``
     in the repository root folder. Use pip to install them:

     .. code::

        pip install -r ./requirements.txt

     Additionally install **LaTeX** (recommended: TeX Live). This is used to render the documentation.

   * Configure dependencies

     The installation of **RobotFramework_UDS** includes to generate the documentation in PDF format. This is done by
     an application called **GenPackageDoc**, that is part of the installation dependencies (see ``requirements.txt``).

     **GenPackageDoc** uses **LaTeX** to generate the documentation in PDF format. Therefore **GenPackageDoc** needs to know where to find
     **LaTeX**. This is defined in the **GenPackageDoc** configuration file

     .. code::

        packagedoc\packagedoc_config.json

     Before you start the installation you have to introduce the following environment variable, that is used in ``packagedoc_config.json``:

     - ``GENDOC_LATEXPATH`` : path to ``pdflatex`` executable

   * Use the following command to install **RobotFramework_UDS**:

     .. code::

        setup.py install


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

Copyright 2020-2024 Robert Bosch GmbH

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

