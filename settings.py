from os import environ

SESSION_CONFIGS = [
    {
        'name': 'pure_colorblind',
        'display_name': 'Pure CB',
        'app_sequence': ['pure_colorblind'],
        'num_demo_participants': 2,
    },
    {
        'name': 'type_disclosure',
        'display_name': 'TD',
        'app_sequence': ['type_disclosure'],
        'num_demo_participants': 2,
    },
    {
        'name': 'costly_signaling',
        'display_name': 'CS',
        'app_sequence': ['costly_signaling'],
        'num_demo_participants': 2,
    },
    {
        'name': 'mixed',
        'display_name': 'CS w/ TD',
        'app_sequence': ['mixed'],
        'num_demo_participants': 2,
   
    },
     {
        'name': 'test',
        'display_name': 'test',
        'app_sequence': ['test'],
        'num_demo_participants': 2,
   
    }
]

SESSION_CONFIG_DEFAULTS = {
    'name': 'My Default Session',
    'participation_fee': 0,
    'display_name': 'Default Session',
    'num_demo_participants': 6,
    'real_world_currency_per_point': 1/7,
    'name': 'training_belief_double_3',
    'display_name': "Training (with belief elicitation) - double 3",
    'num_demo_participants': 6,
    'use_firm_belief_elicitation': True,
    'use_worker_belief_elicitation': True,
    'num_first_stage_rounds': 1,
    'num_second_stage_rounds': 1,
    'num_third_stage_rounds': 1,
    'num_fourth_stage_rounds': 1,
    'third_stage_stipend_green': 0,
    'third_stage_stipend_purple': 0,
    'real_world_currency_per_point': 1/7,
    'app_sequence': ['pure_colorblind'],
    'participation_fee': 100,
}

# Additional oTree configurations and settings go here
LANGUAGE_CODE = 'zh-tw'
USE_POINTS = True
POINTS_CUSTOM_NAME = '法幣'
SECRET_KEY = ''
if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True
DEFAULT_CHARSET = 'UTF-8'

# Define other settings as needed
INSTALLED_APPS = ['otree']
