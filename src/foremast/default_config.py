"""Default Foremast configuration."""
DEFAULT_CONFIG = {
    'base': {
        'ami_json_url': None,
        'default_ec2_securitygroups': {},
        'default_elb_securitygroups': {},
        'default_securitygroup_rules': {},
        'domain': 'example.com',
        'ec2_pipeline_types': [],
        'envs': [],
        'gate_api_url': None,
        'gate_ca_bundle': '',
        'gate_client_cert': '',
        'git_url': None,
        'regions': [],
        'securitygroup_replacements': {},
        'templates_path': None,
        'types': [
            'datapipeline',
            'ec2',
            'lambda',
            'rolling',
            's3',
        ],
    },
    'credentials': {
        'gitlab_token': None,
        'slack_token': None,
    },
    'formats': {},
    'headers': {
        'accept': '*/*',
        'content-type': 'application/json',
        'user-agent': 'foremast',
    },
    'links': {
        'default': {},
    },
    'task_timeouts': {
        'default': 120,
        'envs': {},
    },
    'whitelists': {
        'asg_whitelist': [],
    },
}
