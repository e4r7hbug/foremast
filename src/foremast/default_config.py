"""Default Foremast configuration."""
DEFAULT_CONFIG = {
    'base': {
        'ami_json_url': '',
        'default_ec2_securitygroups': {},
        'default_elb_securitygroups': {},
        'default_securitygroup_rules': {},
        'domain': 'example.com',
        'ec2_pipeline_types': [],
        'envs': [],
        'gate_api_url': '',
        'gate_ca_bundle': '',
        'gate_client_cert': '',
        'git_url': '',
        'regions': [],
        'securitygroup_replacements': {},
        'templates_path': '',
        'types': [
            'datapipeline',
            'ec2',
            'lambda',
            'rolling',
            's3',
        ],
    },
    'credentials': {
        'gitlab_token': '',
        'slack_token': '',
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
