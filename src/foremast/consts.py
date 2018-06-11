#   Foremast - Pipeline Tooling
#
#   Copyright 2018 Gogo, LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Load base config and export package constants.

The ``foremast`` configuration file is read from the following locations in
descending order. First found wins.

* ``./.foremast/foremast.cfg``
* ``~/.foremast/foremast.cfg``
* ``/etc/foremast/foremast.cfg``

.. literalinclude:: ../../src/foremast/templates/configs/foremast.cfg.example
   :language: ini
"""
import logging
from os.path import expanduser, expandvars

from .load_config import CONFIG

LOG = logging.getLogger(__name__)
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s'
SHORT_LOGGING_FORMAT = '[%(levelname)s] %(message)s'

logging.basicConfig(format=LOGGING_FORMAT)
logging.getLogger(__package__.split('.')[0]).setLevel(logging.INFO)

GOOD_STATUSES = frozenset(('SUCCEEDED', ))
SKIP_STATUSES = frozenset(('NOT_STARTED', ))

API_URL = CONFIG['base']['gate_api_url']
GIT_URL = CONFIG['base']['git_url']
DOMAIN = CONFIG['base']['domain']
ENVS = CONFIG['base']['envs']
REGIONS = CONFIG['base']['regions']
ALLOWED_TYPES = CONFIG['base']['types']
TEMPLATES_PATH = CONFIG['base']['templates_path']
AMI_JSON_URL = CONFIG['base']['ami_json_url']
DEFAULT_SECURITYGROUP_RULES = CONFIG['base']['default_securitygroup_rules']
DEFAULT_EC2_SECURITYGROUPS = CONFIG['base']['default_ec2_securitygroups']
DEFAULT_ELB_SECURITYGROUPS = CONFIG['base']['default_elb_securitygroups']
SECURITYGROUP_REPLACEMENTS = CONFIG['base']['securitygroup_replacements']
GITLAB_TOKEN = CONFIG['credentials']['gitlab_token']
SLACK_TOKEN = CONFIG['credentials']['slack_token']
DEFAULT_TASK_TIMEOUT = CONFIG['task_timeouts']['default']
TASK_TIMEOUTS = CONFIG['task_timeouts']['envs']
ASG_WHITELIST = CONFIG['whitelists']['asg_whitelist']
APP_FORMATS = CONFIG['formats']
GATE_CLIENT_CERT = expandvars(expanduser(CONFIG['base']['gate_client_cert']))
GATE_CA_BUNDLE = expandvars(expanduser(CONFIG['base']['gate_ca_bundle']))
LINKS = CONFIG['links']['default']

HEADERS = CONFIG['headers']
