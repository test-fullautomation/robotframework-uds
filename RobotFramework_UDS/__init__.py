#  Copyright 2020-2023 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from RobotFramework_UDS.UDSKeywords import UDSKeywords
from RobotFramework_UDS.version import VERSION


class RobotFramework_UDS(UDSKeywords):
    """
    RobotFramework_UDS is a Robot Framework library aimed to provide UDP client to handle request/response.

    """
    __version__ = VERSION
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
