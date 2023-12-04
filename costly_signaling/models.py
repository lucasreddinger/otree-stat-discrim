#-*- coding: utf-8 -*-
# <standard imports>
from __future__ import division

import random
import math

from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range
)
#import otree.models
#from otree.db import models
#from otree import widgets
#from otree.common import Currency as c, currency_range, safe_json
#from otree.constants import BaseConstants
#from otree.models import BaseSubsession, BaseGroup, BasePlayer

# </standard imports>

author = 'crabbe@hss.caltech.edu'

doc = """
Workers choose whether to invest in training.  Firms can observe the "Color" of workers and decides whether to hire the
worker they are (randomly and anonymously) paired with, then asked how likely it is the worker chose to invest in
training
"""

# {
#         'name': 'training_nobelief',
#         'display_name': "Training (no belief elicitation)",
#         'num_demo_participants': 2,
#         'use_firm_belief_elicitation': False,
#         'use_worker_belief_elicitation': False,
#         'app_sequence': ['training'],
#     },
#     {
#         'name': 'training_belief_double_3',
#         'display_name': "Training (with belief elicitation) - double 3",
#         'num_demo_participants': 2,
#         'use_firm_belief_elicitation': True,
#         'use_worker_belief_elicitation': True,
#         'num_first_stage_rounds': 1,
#         'num_second_stage_rounds': 1,
#         'num_third_stage_rounds': 2,
#         'num_fourth_stage_rounds': 1,
#         'third_stage_stipend_green': 0,
#         'third_stage_stipend_purple': 200,
#         'app_sequence': ['training'],
#     },


class C(BaseConstants):
    NAME_IN_URL = 'costly_signaling'
    # number of players in a group - SHOULD ALWAYS BE 2
    PLAYERS_PER_GROUP = 2
    # the number of rounds to play - should be a multiple of 4
    ##change to 40
    NUM_ROUNDS = 4
    # the costs of training in the different treatments
    ##WW: third round should be color-blind round
    FIRST_COST_OF_TRAINING_GREEN = 200
    FIRST_COST_OF_TRAINING_PURPLE = 600
    SECOND_COST_OF_TRAINING = 200
    THIRD_COST_OF_TRAINING = 200
    FOURTH_COST_OF_TRAINING = 200
    # payoffs for different treatments
    ##WW
    SIGNALING_COST = 10
    WORKER_HIRE_INVEST = 1800
    WORKER_HIRE_NOT_INVEST = 1400
    WORKER_NOT_HIRE_INVEST = 1000
    WORKER_NOT_HIRE_NOT_INVEST = 1200
    FIRM_HIRE_INVEST = 1600
    FIRM_HIRE_NOT_INVEST = 400
    FIRM_NOT_HIRE_INVEST = 1200
    FIRM_NOT_HIRE_NOT_INVEST = 1200
    BIG_PRIZE = 200
    SMALL_PRIZE = 0
    COLORS = ["PURPLE", "GREEN"]

#WW: reassign worker-firm pairings
#def randomize_groups(subsession):
 #   players = subsession.get_players()
  #  random.shuffle(players)
   # group_size = 2  # Adjust this to your group size
    #groups = [players[i:i + group_size] for i in range(0, len(players), group_size)]

    #for i, group in enumerate(groups):
     #   for player in group:
      #      player.group = i + 1  # Assign the group number
    
class Subsession(BaseSubsession):
    green_investment_count = models.IntegerField(initial=0)
    purple_investment_count = models.IntegerField(initial=0)
    green_hiring_count = models.IntegerField(initial=0)
    purple_hiring_count = models.IntegerField(initial=0)

    paying_round = models.IntegerField(initial=-1)
    #WW added following line:
    is_final_round = models.BooleanField(initial=False)
    use_firm_belief_elicitation = models.BooleanField(initial=True)
    use_worker_belief_elicitation = models.BooleanField(initial=True)
    num_first_stage_rounds = models.IntegerField(initial=0)
    num_second_stage_rounds = models.IntegerField(initial=0)
    num_third_stage_rounds = models.IntegerField(initial=0)
    num_fourth_stage_rounds = models.IntegerField(initial=0)
    num_rounds = models.IntegerField(initial=0)

    third_stage_stipend_green = models.IntegerField(initial=0)
    third_stage_stipend_purple = models.IntegerField(initial=0)

    def creating_session(self):
        self.group_randomly(fixed_id_in_group=True)
    # WW: If the current round number is 1, this conditional statement proceeds to create a map that associates round numbers
    # with a boolean value indicating whether it's a paid round or not. This mapping is stored in the variable self.paying_round,
    # and it's generated randomly between rounds 1 and C.NUM_ROUNDS.
        if self.round_number == 1:
            self.paying_round = random.randint(1, C.NUM_ROUNDS)
          #  randomize_groups(self)
# WW: Only shuffle groups at the beginning of each sequence
#WW: else: If the current round is not the first round (i.e., round_number is not 1), it retrieves the paying_round value from the previous round, which is stored in the first element of the list returned by self.in_previous_rounds(). This is done to maintain continuity in paid rounds.
        else:
            self.paying_round = self.in_previous_rounds()[0].paying_round
##WW: The subsequent if statements check for certain configuration options in the self.session.config dictionary. If a configuration option is found, it's assigned to the respective class attribute. For example, self.use_firm_belief_elicitation and self.use_worker_belief_elicitation are set based on the presence of 'use_firm_belief_elicitation' and 'use_worker_belief_elicitation' in the session configuration. Similar checks are done for other parameters like the number of rounds in different stages (self.num_first_stage_rounds, self.num_second_stage_rounds, etc.) and stipend values for the third stage.
        if 'use_firm_belief_elicitation' in self.session.config:
            self.use_firm_belief_elicitation = self.session.config['use_firm_belief_elicitation']

        if 'use_worker_belief_elicitation' in self.session.config:
            self.use_worker_belief_elicitation = self.session.config['use_worker_belief_elicitation']

        if 'num_first_stage_rounds' in self.session.config:
            self.num_first_stage_rounds = self.session.config['num_first_stage_rounds']
        else:
            self.num_first_stage_rounds = 1

        if 'num_second_stage_rounds' in self.session.config:
            self.num_second_stage_rounds = self.session.config['num_second_stage_rounds']
        else:
            self.num_second_stage_rounds = 1

        if 'num_third_stage_rounds' in self.session.config:
            self.num_third_stage_rounds = self.session.config['num_third_stage_rounds']
        else:
            self.num_third_stage_rounds = 1

        if 'num_fourth_stage_rounds' in self.session.config:
            self.num_fourth_stage_rounds = self.session.config['num_fourth_stage_rounds']
        else:
            self.num_fourth_stage_rounds = 1

        self.num_rounds = self.num_first_stage_rounds + self.num_second_stage_rounds + self.num_third_stage_rounds \
                          + self.num_fourth_stage_rounds

        if 'third_stage_stipend_purple' in self.session.config:
            self.third_stage_stipend_purple = self.session.config['third_stage_stipend_purple']
        else:
            self.third_stage_stipend_purple = 200

        if 'third_stage_stipend_green' in self.session.config:
            self.third_stage_stipend_green = self.session.config['third_stage_stipend_green']
        else:
            self.third_stage_stipend_green = 0

        # assign the players into groups, make it so that players with even IDs are always
        # workers and odd IDs are always firms
        if self.round_number > 0:
            odd_players = []
            even_players = []
            for p in self.get_players():
                if p.participant.id_in_session % 2 == 0:
                    even_players.append(p)
                else:
                    odd_players.append(p)
            list_of_lists = []
            random.shuffle(odd_players)
            random.shuffle(even_players)
            num_groups = int(len(self.get_players()) / C.PLAYERS_PER_GROUP)
            # print("len(self.get_players())=" + str(len(self.get_players())) + ", C.PLAYERS_PER_GROUP=" + str(C.PLAYERS_PER_GROUP))
            for g in range(num_groups):
                group_players = [odd_players[g], even_players[g]]
                print("groupnum " + str(g) + ": " + str(group_players))
                list_of_lists.append(group_players)
           # WW: self.set_groups(list_of_lists)
                self.get_group_matrix(list_of_lists)

        # if this is the first round, assign a color to the worker (so that there are even number of each color)
        # and store them in participant.vars so that they can be accessed by the group

        if self.round_number == 1:
            count = 0
            color_list = []
            for g in self.get_groups():
                count += 1
                if count % 3 == 0:
                    color_list.append(C.COLORS[0])  # Append 'GREEN'
                else:
                    color_list.append(C.COLORS[1])  # Append 'PURPLE'
                #color_list.append(C.COLORS[count % 2])
                # print(str(color_list))
            random.shuffle(color_list)
            count = 0

            for g in self.get_groups():
                g.get_player_by_role('Worker').participant.vars['worker_color'] = color_list[count]
                # g.worker_color = color_list[count]
                count += 1
                print(
                    "round_number=" + str(self.round_number) + ", assigning group " + str(
                        g) + " worker color value " + str(
                        g.get_player_by_role('Worker').participant.vars['worker_color']))
                #WW: added
        # retrieve the worker_color set for this group's worker in round 1
        for g in self.get_groups():
            g.worker_color = g.get_player_by_role('Worker').participant.vars['worker_color']
      

        # set up the correct payoff vars and cost_of_training for each group (based on treatment and worker color)
        third_stage_start = (self.num_first_stage_rounds + self.num_second_stage_rounds)
        fourth_stage_start = (self.num_first_stage_rounds + self.num_second_stage_rounds + self.num_third_stage_rounds)
        for g in self.get_groups():
            g.round_num = self.round_number
            g.use_firm_belief = self.use_firm_belief_elicitation
            g.use_worker_belief = self.use_worker_belief_elicitation
            g.stipend = 0
            if 0 < self.round_number <= self.num_first_stage_rounds:
                if g.worker_color == 'GREEN':
                    g.cost_of_training = C.FIRST_COST_OF_TRAINING_GREEN
                elif g.worker_color == 'PURPLE':
                    g.cost_of_training = C.FIRST_COST_OF_TRAINING_PURPLE
            elif self.num_first_stage_rounds < self.round_number <= third_stage_start:
                g.cost_of_training = C.SECOND_COST_OF_TRAINING
            elif third_stage_start < self.round_number <= fourth_stage_start:
                g.cost_of_training = C.THIRD_COST_OF_TRAINING
                if g.worker_color == 'GREEN':
                    g.stipend = self.third_stage_stipend_green
                elif g.worker_color == 'PURPLE':
                    g.stipend = self.third_stage_stipend_purple
            elif fourth_stage_start < self.round_number <= self.num_rounds:
                g.cost_of_training = C.FOURTH_COST_OF_TRAINING


class Group(BaseGroup):
    ##WW:
    send_signal = models.BooleanField(
    #    initial = None,
        doc="""Whether the worker wants to send costly message""",
        verbose_name='您打算傳送「我願意投入受訓」的訊息給雇主嗎? 傳送訊息的成本為10法幣。',
        choices=[
            [True, '是'],  # Maps True to '是'
            [False, '否'],  # Maps False to '否'
        ],
    )
    worker_invest = models.BooleanField(
        initial = None,
        doc="""Whether the worker wants to invest""",
        #WW: verbose_name='Do you wish to invest in training?',
        verbose_name='您打算投入受訓嗎?',
        choices=[
            [True, '是'],  # Maps True to '是'
            [False, '否'],  # Maps False to '否'
        ],
    )
    firm_hire = models.BooleanField(
        initial = None,
        doc="""Whether the firm wants to hire""",
        ##WW: verbose_name='Do you wish to hire the worker?',
        verbose_name='您打算錄取求職者嗎?',
        choices=[
            [True, '是'],  # Maps True to '是'
            [False, '否'],  # Maps False to '否'
        ],
    )
    firm_investment_belief = models.IntegerField(
        initial=-1,
        choices=range(0, 101),
        ##WW: verbose_name='In your view, what is the likelihood that the worker you are paired '
                     ##'with chose to invest in training?',
        verbose_name='據您估計，配對到的求職者有多高機率會投入受訓?',
        #widget=widgets.Slider(
        widget = widgets.RadioSelectHorizontal(
           # attrs={'step': '1',
            #       'min': '-1',
             #      'max': '100'}
        )
    )
    worker_hiring_belief = models.IntegerField(
        initial=-1,
        choices=range(0, 101),
        ##WW: verbose_name='In your view, what is the likelihood that the firm you are paired '
                     ##'with chose to hire you?',
        verbose_name='據您估計，配對到的雇主有多高機率會錄取您?',
       # widget=widgets.Slider(
        widget = widgets.RadioSelectHorizontal(
         #   attrs={'step': '1',
          #         'min': '-1',
           #        'max': '100'}
        )
    )
    task_1 = models.IntegerField(
        initial=-1,
        choices=range(0, 201),
        verbose_name='請問您打算把多少法幣投入抽獎?',
       # widget=widgets.Slider(
        widget = widgets.RadioSelectHorizontal(
         #   attrs={'step': '1',
          #         'min': '-1',
           #        'max': '100'}
        )
    )
    task_2 = models.IntegerField(
        initial=-1,
        choices=range(0, 201),
        verbose_name='請問您打算把多少法幣投入抽獎?',
       # widget=widgets.Slider(
        widget = widgets.RadioSelectHorizontal(
         #   attrs={'step': '1',
          #         'min': '-1',
           #        'max': '100'}
        )
    )
    firm_belief_payoff = models.CurrencyField(
        initial=0,
    )
    firm_normal_payoff = models.CurrencyField(
        initial=0,
    )
    worker_belief_payoff = models.CurrencyField(
        initial=0,
    )
    worker_normal_payoff = models.CurrencyField(
        initial=0,
    )
    worker_color = models.StringField()
    cost_of_training = models.IntegerField()
    stipend = models.IntegerField()
    # the current round number because you can't access that info from the Constants on the actual pages
    round_num = models.IntegerField()
    # whether or not to ask the firm for their belief of how likely the worker invested
    use_firm_belief = models.BooleanField()
    use_worker_belief = models.BooleanField()

    # the output should reveal the rates that the players see
    green_invest_rate_shown = models.StringField()
    purple_invest_rate_shown = models.StringField()
    green_hire_rate_shown = models.StringField()
    purple_hire_rate_shown = models.StringField()
    ##WW: added
    avg_invest_rate_shown =  models.StringField()
    avg_hire_rate_shown = models.StringField()

    def set_payoffs(self):
        firm = self.get_player_by_role('Firm')
        worker = self.get_player_by_role('Worker')
        if self.field_maybe_none('send_signal') is None:
            if self.worker_invest and self.firm_hire:
                worker.potential_payoff = (C.WORKER_HIRE_INVEST - self.cost_of_training)
                firm.potential_payoff = (C.FIRM_HIRE_INVEST + self.stipend)
            elif self.worker_invest and not self.firm_hire:
                worker.potential_payoff = (C.WORKER_NOT_HIRE_INVEST - self.cost_of_training)
                firm.potential_payoff = (C.FIRM_NOT_HIRE_INVEST)
            elif not self.worker_invest and self.firm_hire:
                worker.potential_payoff = (C.WORKER_HIRE_NOT_INVEST)
                firm.potential_payoff = (C.FIRM_HIRE_NOT_INVEST + self.stipend)
            elif not self.worker_invest and not self.firm_hire:
                worker.potential_payoff = (C.WORKER_NOT_HIRE_NOT_INVEST)
                firm.potential_payoff = (C.FIRM_NOT_HIRE_NOT_INVEST)
        elif self.field_maybe_none('send_signal'):
            if self.worker_invest and self.firm_hire:
                worker.potential_payoff = (C.WORKER_HIRE_INVEST - self.cost_of_training-C.SIGNALING_COST)
                firm.potential_payoff = (C.FIRM_HIRE_INVEST + self.stipend)
            elif self.worker_invest and not self.firm_hire:
                worker.potential_payoff = (C.WORKER_NOT_HIRE_INVEST - self.cost_of_training-C.SIGNALING_COST)
                firm.potential_payoff = (C.FIRM_NOT_HIRE_INVEST)
            elif not self.worker_invest and self.firm_hire:
                worker.potential_payoff = (C.WORKER_HIRE_NOT_INVEST-C.SIGNALING_COST)
                firm.potential_payoff = (C.FIRM_HIRE_NOT_INVEST + self.stipend)
            elif not self.worker_invest and not self.firm_hire:
                worker.potential_payoff = (C.WORKER_NOT_HIRE_NOT_INVEST-C.SIGNALING_COST)
                firm.potential_payoff = (C.FIRM_NOT_HIRE_NOT_INVEST)
        else: 
            if self.worker_invest and self.firm_hire:
                worker.potential_payoff = (C.WORKER_HIRE_INVEST - self.cost_of_training)
                firm.potential_payoff = (C.FIRM_HIRE_INVEST + self.stipend)
            elif self.worker_invest and not self.firm_hire:
                worker.potential_payoff = (C.WORKER_NOT_HIRE_INVEST - self.cost_of_training)
                firm.potential_payoff = (C.FIRM_NOT_HIRE_INVEST)
            elif not self.worker_invest and self.firm_hire:
                worker.potential_payoff = (C.WORKER_HIRE_NOT_INVEST)
                firm.potential_payoff = (C.FIRM_HIRE_NOT_INVEST + self.stipend)
            elif not self.worker_invest and not self.firm_hire:
                worker.potential_payoff = (C.WORKER_NOT_HIRE_NOT_INVEST)
                firm.potential_payoff = (C.FIRM_NOT_HIRE_NOT_INVEST)

        self.firm_normal_payoff = firm.potential_payoff
        self.worker_normal_payoff = worker.potential_payoff
        print("firm_payoff=" + str(firm.potential_payoff) + ", worker_payoff=" + str(worker.potential_payoff))

        if self.use_firm_belief:
            if self.worker_invest:
                probability = 1 - math.pow(1 - self.firm_investment_belief / 100, 2)
                print(
                    "worker invested, firm_investment_belief=" + str(
                        self.firm_investment_belief) + ", probability=" + str(
                        probability))
            else:
                probability = 1 - math.pow(self.firm_investment_belief / 100, 2)
                print("worker did not invest, firm_investment_belief=" + str(
                    self.firm_investment_belief) + ", probability=" + str(probability))
            if random.random() < probability:
                print("firm wins big belief elicitation prize: " + str(C.BIG_PRIZE))
                self.firm_belief_payoff = C.BIG_PRIZE
                firm.potential_payoff += C.BIG_PRIZE
            else:
                print("firm wins small belief elicitation prize: " + str(C.SMALL_PRIZE))
                self.firm_belief_payoff = C.SMALL_PRIZE
                firm.potential_payoff += C.SMALL_PRIZE

        if self.use_worker_belief:
            if self.worker_invest:
                probability = 1 - math.pow(1 - self.worker_hiring_belief / 100, 2)
                print(
                    "worker invested, worker_hiring_belief=" + str(
                        self.worker_hiring_belief) + ", probability=" + str(probability))
            else:
                probability = 1 - math.pow(self.worker_hiring_belief / 100, 2)
                print("worker did not invest, worker_hiring_belief=" + str(
                    self.worker_hiring_belief) + ", probability=" + str(probability))
            if random.random() < probability:
                print("worker wins big belief elicitation prize: " + str(C.BIG_PRIZE))
                self.worker_belief_payoff = C.BIG_PRIZE
                worker.potential_payoff += C.BIG_PRIZE
            else:
                print("worker wins small belief elicitation prize: " + str(C.SMALL_PRIZE))
                self.worker_belief_payoff = C.SMALL_PRIZE
                worker.potential_payoff += C.SMALL_PRIZE

        print("setting payoffs: subsession.paying_round=" + str(self.subsession.paying_round))
        if self.subsession.round_number == self.subsession.num_rounds:
            firm.payoff = firm.in_round(self.subsession.paying_round).potential_payoff
            worker.payoff = worker.in_round(self.subsession.paying_round).potential_payoff


class Player(BasePlayer):
    def role(self):
        if self.id_in_group == 1:
            return 'Worker'
        if self.id_in_group == 2:
            return 'Firm'

    potential_payoff = models.CurrencyField(
        initial=0
    )
