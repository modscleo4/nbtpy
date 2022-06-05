# A Python 3 NBT (Named Binary Tag) Parser
#
# Copyright 2022 Dhiego Cassiano Fogaça Barbosa <modscleo4@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from configparser import ConfigParser


class Settings:
    '''
    Settings wrapper
    '''

    config: ConfigParser = ConfigParser()
    '''
    INI parser
    '''

    debug: bool = False
    '''
    Print debug information
    '''

    format: bool = True
    '''
    If the SNBT string should be formatted
    '''

    log_path: str = '/tmp/nbtpy.log'
    '''
    Where to store log file
    '''

    def __init__(self, FILE: str = '/etc/nbtpy.conf') -> None:
        self.config.read(FILE)
        self.debug = self.config.getboolean('General', 'DEBUG', fallback=False)
        self.log_path = self.config.get('General', 'LOG_PATH', fallback='/tmp/nbtpy.log')
        self.format = self.config.getboolean('Output', 'FORMAT', fallback=True)

    def __repr__(self) -> str:
        return f"[General]\n"\
            f"  Debug: {self.debug}\n"\
            f"[Output]\n"\
            f"  Format: {self.format}"


settings = Settings()
