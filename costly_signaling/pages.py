#-*- coding: utf-8 -*-
from __future__ import division

from otree.api import *
#from otree.common import Currency as c, currency_range, safe_json
import random
import math
from ._builtin import Page, WaitPage
#from .models import Constants
#from . import models
#from otree.channels.routing import channel_routing;
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

class C(BaseConstants):
    NAME_IN_URL = 'costly_signaling'
    # number of players in a group - SHOULD ALWAYS BE 2
    PLAYERS_PER_GROUP = 2
    # the number of rounds to play - should be a multiple of 4
    NUM_ROUNDS = 4
    # the costs of training in the different treatments
    FIRST_COST_OF_TRAINING_GREEN = 200
    FIRST_COST_OF_TRAINING_PURPLE = 600
    SECOND_COST_OF_TRAINING = 200
    THIRD_COST_OF_TRAINING = 200
    FOURTH_COST_OF_TRAINING = 200
    # payoffs for different treatments
    ##WW:
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
    
class Signal(Page):
    form_model = 'group'
    form_fields = ['send_signal']

    def vars_for_template(self):
        green_invest_count = 0.
        purple_invest_count = 0.
        green_hiring_count = 0.
        purple_hiring_count = 0.
        green_count = 0
        purple_count = 0
        for s in self.subsession.in_previous_rounds():
            # print("subsession " + str(s))
            for g in s.get_groups():
                # print("group "+str(g)+", g.worker_color="+str(g.worker_color)+", g.worker_invest="+str(g.worker_invest)+", g.firm_hire="+str(g.firm_hire))

                if g.worker_color == 'GREEN':
                    green_count += 1
                    if g.worker_invest:
                        green_invest_count += 1
                        # print("green_invest_count="+str(green_invest_count))
                    if g.firm_hire:
                        green_hiring_count += 1
                        # print("green_hiring_count=" + str(green_hiring_count))
                elif g.worker_color == 'PURPLE':
                    purple_count += 1
                    if g.worker_invest:
                        purple_invest_count += 1
                        # print("purple_invest_count=" + str(purple_invest_count))
                    if g.firm_hire:
                        purple_hiring_count += 1
                        # print("purple_hiring_count=" + str(purple_hiring_count))
        if green_count == 0:
            self.group.green_invest_rate_shown = '0.0'
            self.group.green_hire_rate_shown = '0.0'
        else:
            self.group.green_invest_rate_shown = str(round(green_invest_count / green_count, 2))
            self.group.green_hire_rate_shown = str(round(green_hiring_count / green_count, 2))

        if purple_count == 0:
            self.group.purple_invest_rate_shown = '0.0'
            self.group.purple_hire_rate_shown = '0.0'
        else:
            self.group.purple_invest_rate_shown = str(round(purple_invest_count / purple_count, 2))
            self.group.purple_hire_rate_shown = str(round(purple_hiring_count / purple_count, 2))
          
            
            ##WW:
        if purple_count + green_count == 0:
            self.group.avg_hire_rate_shown = '0.0'
            self.group.avg_invest_rate_shown = '0.0'
        else:
            self.group.avg_hire_rate_shown = str(round((purple_hiring_count + green_hiring_count)/(green_count+purple_count) , 2))
            self.group.avg_invest_rate_shown = str(round((purple_invest_count + green_invest_count)/(green_count+purple_count) , 2))
            # print("views.Firm:  group=" + str(self.group) + ", self.group.worker_color=" + str(self.group.worker_color))

        table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
        table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
        table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
        table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        second_stage_start = self.subsession.num_first_stage_rounds
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        fourth_stage_start = (
            self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        if third_stage_start < self.subsession.round_number <= fourth_stage_start and self.group.worker_color == 'PURPLE':
            table_invest_hire = "{0} - c, {1} + s".format(str(C.WORKER_HIRE_INVEST),
                                                          str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1} + s".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                          str(C.FIRM_HIRE_NOT_INVEST))

        green_cost = 0
        purple_cost = 0
        extra_text_green = ""
        extra_text_purple = ""
        extra_text_type = ""
        instructions_text = ""
        instructions_text_2 = ""
        instructions_text_3 = ""

        stage_num = 0
        if 0 < self.round_number <= second_stage_start:
            green_cost = C.FIRST_COST_OF_TRAINING_GREEN
            purple_cost = C.FIRST_COST_OF_TRAINING_PURPLE
            stage_num = 1
            stage_round = self.round_number
        elif second_stage_start < self.round_number <= third_stage_start:
            green_cost = C.SECOND_COST_OF_TRAINING
            purple_cost = C.SECOND_COST_OF_TRAINING
            stage_num = 2
            stage_round = self.round_number - second_stage_start
        elif third_stage_start < self.round_number <= fourth_stage_start:
            green_cost = C.THIRD_COST_OF_TRAINING
            purple_cost = C.THIRD_COST_OF_TRAINING
            stage_num = 3
            stage_round = self.round_number - third_stage_start
        elif fourth_stage_start < self.round_number <= self.subsession.num_rounds:
            green_cost = C.FOURTH_COST_OF_TRAINING
            purple_cost = C.FOURTH_COST_OF_TRAINING
            stage_num = 4
            stage_round = self.round_number - fourth_stage_start
        return {
            'table_invest_hire': str(table_invest_hire),
            'table_invest_not_hire': str(table_invest_not_hire),
            'table_not_invest_hire': str(table_not_invest_hire),
            'table_not_invest_not_hire': str(table_not_invest_not_hire),
            'green_invest_rate': self.group.green_invest_rate_shown,
            'purple_invest_rate': self.group.purple_invest_rate_shown,
            'green_hiring_rate': self.group.green_hire_rate_shown,
            'purple_hiring_rate': self.group.purple_hire_rate_shown,
            'green_invest_count': str(green_invest_count),
            'purple_invest_count': str(purple_invest_count),
            'green_hiring_count': str(green_hiring_count),
            'purple_hiring_count': str(purple_hiring_count),
              ##WW:
            'avg_hiring_rate': self.group.avg_hire_rate_shown,
            'avg_invest_rate': self.group.avg_invest_rate_shown,
            'worker_color': str(self.group.worker_color),
            'cost_of_training': str(self.group.cost_of_training),
            'graph_purple_invest_rate': safe_json(self.group.purple_invest_rate_shown),
            'graph_green_invest_rate': safe_json(self.group.green_invest_rate_shown),
            'graph_purple_hiring_rate': safe_json(self.group.purple_hire_rate_shown),
            'graph_green_hiring_rate': safe_json(self.group.green_hire_rate_shown),
            'purple_cost': str(purple_cost),
            'green_cost': str(green_cost),
            'extra_text_green': str(extra_text_green),
            'extra_text_purple': str(extra_text_purple),
            'extra_text_type': str(extra_text_type),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round)
        }
    def is_displayed(self):
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        return self.player.id_in_group == 1 and self.round_number > third_stage_start

class WaitForWorkers(WaitPage):
    wait_for_all_groups = False  # Set this to False to only wait for paired workers
    
    title_text = ""
    body_text = "請稍待其他玩家做決策，謝謝" 
    def is_displayed(self):
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        return self.player.id_in_group == 2 and self.round_number > third_stage_start
            
        
class Worker(Page):
    form_model = 'group'

    def is_displayed(self):
        return self.player.id_in_group == 1 and self.round_number <= self.subsession.num_rounds

    def get_form_fields(self):
        if self.subsession.use_worker_belief_elicitation:
            return ['worker_invest', 'worker_hiring_belief']
        else:
            return ['worker_invest']

    def vars_for_template(self):

        green_invest_count = 0.
        purple_invest_count = 0.
        green_hiring_count = 0.
        purple_hiring_count = 0.
        green_count = 0
        purple_count = 0
        for s in self.subsession.in_previous_rounds():
            print("subsession " + str(s))
            for g in s.get_groups():
                print("group " + str(g) + ", g.worker_color=" + str(g.worker_color) + ", g.worker_invest=" + str(
                    g.worker_invest) + ", g.firm_hire=" + str(g.firm_hire))
                if g.worker_color == 'GREEN':
                    green_count += 1
                    if g.worker_invest:
                        green_invest_count += 1
                        print("green_invest_count=" + str(green_invest_count))
                    if g.firm_hire:
                        green_hiring_count += 1
                        print("green_hiring_count=" + str(green_hiring_count))
                elif g.worker_color == 'PURPLE':
                    purple_count += 1
                    if g.worker_invest:
                        purple_invest_count += 1
                        print("purple_invest_count=" + str(purple_invest_count))
                    if g.firm_hire:
                        purple_hiring_count += 1
                        print("purple_hiring_count=" + str(purple_hiring_count))
        if green_count == 0:
            green_count = 1
        if purple_count == 0:
            purple_count = 1

        self.group.green_invest_rate_shown = str(round(green_invest_count / green_count, 2))
        self.group.purple_invest_rate_shown = str(round(purple_invest_count / purple_count, 2))
        self.group.green_hire_rate_shown = str(round(green_hiring_count / green_count, 2))
        self.group.purple_hire_rate_shown = str(round(purple_hiring_count / purple_count, 2))
##WW: 
        self.group.avg_hire_rate_shown = str(round((purple_hiring_count + green_hiring_count)/(green_count+purple_count), 2))
        self.group.avg_invest_rate_shown = str(round((purple_invest_count + green_invest_count)/(green_count+purple_count) , 2))
        print("views.Worker:  group=" + str(self.group) + ", self.group.worker_color=" + str(self.group.worker_color))

        table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
        table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
        table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
        table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        second_stage_start = self.subsession.num_first_stage_rounds
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        fourth_stage_start = (
            self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        if third_stage_start < self.subsession.round_number <= fourth_stage_start and self.group.worker_color == 'PURPLE':
            table_invest_hire = "{0} - c, {1} + s".format(str(C.WORKER_HIRE_INVEST),
                                                          str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1} + s".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                          str(C.FIRM_HIRE_NOT_INVEST))

        green_cost = 0
        purple_cost = 0
        extra_text_green = ""
        extra_text_purple = ""
        worker_send_signal = ""

        stage_num = 0
        if 0 < self.round_number <= second_stage_start:
            green_cost = C.FIRST_COST_OF_TRAINING_GREEN
            purple_cost = C.FIRST_COST_OF_TRAINING_PURPLE
            stage_num = 1
            stage_round = self.round_number
        elif second_stage_start < self.round_number <= third_stage_start:
            green_cost = C.SECOND_COST_OF_TRAINING
            purple_cost = C.SECOND_COST_OF_TRAINING
            stage_num = 2
            stage_round = self.round_number - second_stage_start
        elif third_stage_start < self.round_number <= fourth_stage_start:
            green_cost = C.THIRD_COST_OF_TRAINING
            purple_cost = C.THIRD_COST_OF_TRAINING
            #WW:
            
       #WW: commented out     "extra_text_green = "If a firm hires a GREEN worker, the firm earns a subsidy of " + \"
            extra_text_green = " " #+ \
                   #            str(self.subsession.third_stage_stipend_green) + " (s = " + str(self.subsession.third_stage_stipend_green) + ")"
       #WW: commented out      extra_text_purple = "If a firm hires a PURPLE worker, the firm earns a subsidy of " + \
            extra_text_purple = " " #+ \
                  #              str(self.subsession.third_stage_stipend_purple) + " (s = " + str(self.subsession.third_stage_stipend_purple) + ")"
            stage_num = 3
            stage_round = self.round_number - third_stage_start
        elif fourth_stage_start / 4 < self.round_number:
            green_cost = C.FOURTH_COST_OF_TRAINING
            purple_cost = C.FOURTH_COST_OF_TRAINING
            stage_num = 4
            stage_round = self.round_number - fourth_stage_start

            
        if third_stage_start < self.round_number:
            worker_choose_send = self.group.send_signal
            if worker_choose_send:
                worker_send_signal= "您決定向雇主傳送「我會投入受訓」之訊息。"              
                table_invest_hire = "{0} - c - 10, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0} - 10, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c - 10, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0} - 10,{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
            else:
                worker_send_signal= "您決定不向雇主傳送「我會投入受訓」之訊息。"               
                table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        else:
            worker_choose_send = ""         
            table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
            table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
            table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
        
        return {
            'table_invest_hire': str(table_invest_hire),
            'table_invest_not_hire': str(table_invest_not_hire),
            'table_not_invest_hire': str(table_not_invest_hire),
            'table_not_invest_not_hire': str(table_not_invest_not_hire),
            'green_invest_rate': self.group.green_invest_rate_shown,
            'purple_invest_rate': self.group.purple_invest_rate_shown,
            'green_hiring_rate': self.group.green_hire_rate_shown,
            'purple_hiring_rate': self.group.purple_hire_rate_shown,
                ##WW:
            'worker_choose_send': worker_choose_send,
            'worker_send_signal': str(worker_send_signal),
            'avg_hiring_rate': self.group.avg_hire_rate_shown,
            'avg_invest_rate': self.group.avg_invest_rate_shown,
            'green_invest_count': str(green_invest_count),
            'purple_invest_count': str(purple_invest_count),
            'green_hiring_count': str(green_hiring_count),
            'purple_hiring_count': str(purple_hiring_count),
            'worker_color': str(self.group.worker_color),
            'cost_of_training': str(self.group.cost_of_training),
            'purple_cost': str(purple_cost),
            'green_cost': str(green_cost),
            'extra_text_green': str(extra_text_green),
            'extra_text_purple': str(extra_text_purple),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round)
        }



class Firm(Page):
    form_model = 'group'

    def get_form_fields(self):
        if self.subsession.use_firm_belief_elicitation:
            return ['firm_hire', 'firm_investment_belief']
        else:
            return ['firm_hire']

    def vars_for_template(self):

        green_invest_count = 0.
        purple_invest_count = 0.
        green_hiring_count = 0.
        purple_hiring_count = 0.
        green_count = 0
        purple_count = 0
        for s in self.subsession.in_previous_rounds():
            # print("subsession " + str(s))
            for g in s.get_groups():
                # print("group "+str(g)+", g.worker_color="+str(g.worker_color)+", g.worker_invest="+str(g.worker_invest)+", g.firm_hire="+str(g.firm_hire))

                if g.worker_color == 'GREEN':
                    green_count += 1
                    if g.worker_invest:
                        green_invest_count += 1
                        # print("green_invest_count="+str(green_invest_count))
                    if g.firm_hire:
                        green_hiring_count += 1
                        # print("green_hiring_count=" + str(green_hiring_count))
                elif g.worker_color == 'PURPLE':
                    purple_count += 1
                    if g.worker_invest:
                        purple_invest_count += 1
                        # print("purple_invest_count=" + str(purple_invest_count))
                    if g.firm_hire:
                        purple_hiring_count += 1
                        # print("purple_hiring_count=" + str(purple_hiring_count))
        if green_count == 0:
            self.group.green_invest_rate_shown = '0.0'
            self.group.green_hire_rate_shown = '0.0'
        else:
            self.group.green_invest_rate_shown = str(round(green_invest_count / green_count, 2))
            self.group.green_hire_rate_shown = str(round(green_hiring_count / green_count, 2))

        if purple_count == 0:
            self.group.purple_invest_rate_shown = '0.0'
            self.group.purple_hire_rate_shown = '0.0'
        else:
            self.group.purple_invest_rate_shown = str(round(purple_invest_count / purple_count, 2))
            self.group.purple_hire_rate_shown = str(round(purple_hiring_count / purple_count, 2))
          
            
            ##WW:
        if purple_count + green_count == 0:
            self.group.avg_hire_rate_shown = '0.0'
            self.group.avg_invest_rate_shown = '0.0'
        else:
            self.group.avg_hire_rate_shown = str(round((purple_hiring_count + green_hiring_count)/(green_count+purple_count) , 2))
            self.group.avg_invest_rate_shown = str(round((purple_invest_count + green_invest_count)/(green_count+purple_count) , 2))
            # print("views.Firm:  group=" + str(self.group) + ", self.group.worker_color=" + str(self.group.worker_color))

        second_stage_start = self.subsession.num_first_stage_rounds
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        fourth_stage_start = (
            self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        if third_stage_start < self.subsession.round_number <= fourth_stage_start and self.group.worker_color == 'PURPLE':
            table_invest_hire = "{0} - c, {1} + s".format(str(C.WORKER_HIRE_INVEST),
                                                          str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1} + s".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                          str(C.FIRM_HIRE_NOT_INVEST))

        green_cost = 0
        purple_cost = 0
        extra_text_green = ""
        extra_text_purple = ""
        extra_text_type = ""
        firm_see_signal = ""
        instructions_text = ""
        instructions_text_2 = ""
        instructions_text_3 = ""

        stage_num = 0
        if 0 < self.round_number <= second_stage_start:
            green_cost = C.FIRST_COST_OF_TRAINING_GREEN
            purple_cost = C.FIRST_COST_OF_TRAINING_PURPLE
            stage_num = 1
            stage_round = self.round_number
            #WW:
            extra_text_type = "您被配對到" + str(self.group.worker_color) + "的求職者。"
        elif second_stage_start < self.round_number <= third_stage_start:
            green_cost = C.SECOND_COST_OF_TRAINING
            purple_cost = C.SECOND_COST_OF_TRAINING
            stage_num = 2
            stage_round = self.round_number - second_stage_start
            extra_text_type = "您被配對到" + str(self.group.worker_color) + "的求職者。"
        elif third_stage_start < self.round_number <= fourth_stage_start:
            green_cost = C.THIRD_COST_OF_TRAINING
            purple_cost = C.THIRD_COST_OF_TRAINING
   #         extra_text_green = "If a firm hires a GREEN worker, the firm earns a subsidy of " + \
                           #    str(self.subsession.third_stage_stipend_green) + " (s = " + str(self.subsession.third_stage_stipend_green) + #")"
    #        extra_text_purple = "If a firm hires a PURPLE worker, the firm earns a subsidy of " + \
                          #      str(self.subsession.third_stage_stipend_purple) + " (s = " + str(self.subsession.third_stage_stipend_purple) #+ ")"
            stage_num = 3
            stage_round = self.round_number - third_stage_start
        elif fourth_stage_start < self.round_number <= self.subsession.num_rounds:
            green_cost = C.FOURTH_COST_OF_TRAINING
            purple_cost = C.FOURTH_COST_OF_TRAINING
            stage_num = 4
            stage_round = self.round_number - fourth_stage_start
            
        if third_stage_start < self.round_number:            
            worker_choose_send = self.group.send_signal
            if worker_choose_send:
                firm_see_signal= "您配對到的求職者決定向您傳送「我願意投入受訓」之訊息。"
                table_invest_hire = "{0} - c - 10, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0} - 10, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c - 10, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0}-10,{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
            else:
                firm_see_signal= "您配對到的求職者決定不向您傳送「我願意投入受訓」之訊息。"
                table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
                table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
                table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
                table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))

        else:
            worker_choose_send = ""
            firm_see_signal = ""
            table_invest_hire = "{0} - c, {1}".format(str(C.WORKER_HIRE_INVEST), str(C.FIRM_HIRE_INVEST))
            table_not_invest_hire = "{0}, {1}".format(str(C.WORKER_HIRE_NOT_INVEST),
                                                  str(C.FIRM_HIRE_NOT_INVEST))
            table_invest_not_hire = "{0} - c, {1}".format(str(C.WORKER_NOT_HIRE_INVEST),
                                                      str(C.FIRM_NOT_HIRE_INVEST))
            table_not_invest_not_hire = "{0},{1}".format(str(C.WORKER_NOT_HIRE_NOT_INVEST),
                                                     str(C.FIRM_NOT_HIRE_NOT_INVEST))
            
        return {
            'table_invest_hire': str(table_invest_hire),
            'table_invest_not_hire': str(table_invest_not_hire),
            'table_not_invest_hire': str(table_not_invest_hire),
            'table_not_invest_not_hire': str(table_not_invest_not_hire),
            'green_invest_rate': self.group.green_invest_rate_shown,
            'purple_invest_rate': self.group.purple_invest_rate_shown,
            'green_hiring_rate': self.group.green_hire_rate_shown,
            'purple_hiring_rate': self.group.purple_hire_rate_shown,
            'green_invest_count': str(green_invest_count),
            'purple_invest_count': str(purple_invest_count),
            'green_hiring_count': str(green_hiring_count),
            'purple_hiring_count': str(purple_hiring_count),
              ##WW:
            'worker_choose_send': worker_choose_send,
            'firm_see_signal': firm_see_signal,
            'avg_hiring_rate': self.group.avg_hire_rate_shown,
            'avg_invest_rate': self.group.avg_invest_rate_shown,
            'worker_color': str(self.group.worker_color),
            'cost_of_training': str(self.group.cost_of_training),
            'graph_purple_invest_rate': safe_json(self.group.purple_invest_rate_shown),
            'graph_green_invest_rate': safe_json(self.group.green_invest_rate_shown),
            'graph_purple_hiring_rate': safe_json(self.group.purple_hire_rate_shown),
            'graph_green_hiring_rate': safe_json(self.group.green_hire_rate_shown),
            'purple_cost': str(purple_cost),
            'green_cost': str(green_cost),
            'extra_text_green': str(extra_text_green),
            'extra_text_purple': str(extra_text_purple),
            'extra_text_type': str(extra_text_type),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round)
        }

    def is_displayed(self):
        return self.player.id_in_group == 2 and self.round_number <= self.subsession.num_rounds


class Instructions(Page):
    ##WW:added form_model and form_fields
    form_model = ''  # This will hide the "Next" button on the final round.
    form_fields = []
    def is_displayed(self):
        second_stage_start = self.subsession.num_first_stage_rounds
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        fourth_stage_start = (
            self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        return self.round_number == second_stage_start or self.round_number == third_stage_start or self.round_number == fourth_stage_start ##WW:commented out or self.round_number == self.subsession.num_rounds" 

    def vars_for_template(self):

        instructions_text = ""
        instructions_text_2 = ""
        instructions_text_3 = ""
        second_stage_start = self.subsession.num_first_stage_rounds
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        fourth_stage_start = (
            self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)
        if self.round_number == second_stage_start:
                instructions_text = "您即將進入實驗的第一階段。"
                instructions_text_2 = "本階段 GREEN 求職者的受訓成本為 200 法幣 (c = 200)，PURPLE 求職者的投資成本為 600 法幣 (c = 600)。"   
        elif self.round_number == third_stage_start:
                instructions_text = "您即將進入實驗的第二階段。"
                instructions_text_2 = "本階段所有求職者的受訓成本為 200 法幣 (c = 200)。"
        elif self.round_number == fourth_stage_start:
                  #WW: commented out "instructions_text = "You are entering Stage 3 of the experiment.""
                instructions_text = "您即將進入實驗的第三階段。"
                instructions_text_2 = "本階段所有求職者的受訓成本為 200 法幣 (c = 200)。"
                instructions_text_3 = "本階段雇主不會看見配對到的求職者之類別，但求職者可以傳送「我願意投入受訓」的訊息，訊息成本為10法幣。"
           
        elif self.round_number == self.subsession.num_rounds:
             #WW: commented out "  instructions_text = "You have finished the main portion of the experiment.  You will now be asked to complete two short tasks.  One of these two tasks will be randomly selected for payment.  Your earnings from the randomly selected task will be added to your total earnings from the experiment.""
                instructions_text = "您即將進入實驗的第四階段。"
                instructions_text_2 = "本階段所有求職者的受訓成本為 200 法幣 (c = 200)。"
                instructions_text_3 = "本階段雇主不會看見配對到的求職者之類別，但求職者可以傳送「我願意投入受訓」的訊息，訊息成本為10法幣。"

        return {
            'instructions_text': instructions_text,
            'instructions_text_2': instructions_text_2,
            'instructions_text_3': instructions_text_3
        }


class ResultsWaitPage(WaitPage):
    title_text = ""
    body_text = "請稍待其他玩家做決策，謝謝!"
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class SessionWideWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = ""
    body_text = "請稍待其他玩家做決策，謝謝!"


class Results(Page):
    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def vars_for_template(self):
        print("views.py:  firm_payoff=" + str(
            self.group.get_player_by_role('Firm').potential_payoff) + ", worker_payoff=" + str(
            self.group.get_player_by_role('Worker').potential_payoff))
        second_stage_start = self.subsession.num_first_stage_rounds
        third_stage_start = (self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds)
        fourth_stage_start = (
            self.subsession.num_first_stage_rounds + self.subsession.num_second_stage_rounds + self.subsession.num_third_stage_rounds)

        if 0 < self.round_number <= second_stage_start:
            stage_num = 1
            stage_round = self.round_number
        elif second_stage_start < self.round_number <= third_stage_start:
            stage_num = 2
            stage_round = self.round_number - second_stage_start
        elif third_stage_start < self.round_number <= fourth_stage_start:
            stage_num = 3
            stage_round = self.round_number - third_stage_start
        elif fourth_stage_start < self.round_number <= self.subsession.num_rounds:
            stage_num = 4
            stage_round = self.round_number - fourth_stage_start

        return {
            'firm_belief_payoff': str(self.group.firm_belief_payoff),
            'firm_payoff': str(self.group.get_player_by_role('Firm').potential_payoff),
            'firm_normal_payoff': str(self.group.firm_normal_payoff),
            'worker_belief_payoff': str(self.group.worker_belief_payoff),
            'worker_payoff': str(self.group.get_player_by_role('Worker').potential_payoff),
            'worker_normal_payoff': str(self.group.worker_normal_payoff),
            'stage_num': str(stage_num),
            'stage_round': str(stage_round),
            'worker_color': str(self.group.worker_color)
        }

class Task_Intro(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    def vars_for_template(self):
        task_instructions_text = "接下來，請決定要將多少法幣投入抽獎。"
        return {
            'task_instructions_text': task_instructions_text
        }

class Task(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    form_model = 'group'
    form_fields = ['task_1', 'task_2']

class Payoffs(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds
    def vars_for_template(self):
        choose_task = random.randint(1, 2)
        task_payoff = 0
        if self.group.task_1 >= 0 and self.group.task_2 >= 0 and choose_task == 1:
            lottery_1 = random.randint(1, 2)
            if lottery_1 == 1:              
                task_payoff = self.group.task_1*2.5 + 200 - self.group.task_1
            else:
                task_payoff = 200 - self.group.task_1
        elif self.group.task_1 >= 0 and self.group.task_2 >= 0 and choose_task == 2:
            lottery_2 = random.randint(1, 10)
            if lottery_2 <= 4:              
                task_payoff = self.group.task_2*3 + 200 - self.group.task_2
            else:
                task_payoff = 200 - self.group.task_2
        participation_fee = self.session.config['participation_fee']  # Access the participation_fee from the session config
        total_points = self.participant.payoff
        points_into_currency = (self.participant.payoff+task_payoff)/7
        total_payoff = points_into_currency+self.session.config['participation_fee']
        return {
            'participation_fee': f'${participation_fee:.0f}',
            'total_payoff': f'${total_payoff:.0f}',
            'total_points': str(total_points),
            'points_into_currency': f'${points_into_currency:.0f}',
            'task_payoff': str(task_payoff)
        }

page_sequence = [
    Instructions,
    Signal,
    WaitForWorkers,
    Worker,
    Firm,
    ResultsWaitPage,
    Results,
    SessionWideWaitPage,
    Task_Intro,
    Task,
    Payoffs
]
