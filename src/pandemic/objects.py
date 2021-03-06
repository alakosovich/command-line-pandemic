# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 08:32:15 2021

@author: Alexander Lakocy
"""

import random
from constants import (ACTIONS_PER_TURN,
                       CUBE_LIMIT,
                       MAX_CARDS_IN_HAND,
                       CARDS_TO_CURE,
                       )

from initialize import roles

global cities

class CardDeck(object):
    def __init__(self, card_list):
        self.cards = card_list

    def shuffle(self):
        if self.cards == None:
            return
        cc_card_list = []
        l = len(self.cards)
        for i in range(l):
            ind = random.randint(0, l - i - 1)
            cc_card_list.append(self.cards.pop(ind))
        self.cards = cc_card_list

    def draw_top(self):
        if self.cards == None:
            return
        c = self.cards[0]
        self.remove_card(c)
        return c

    def draw_bot(self):
        if self.cards == None:
            return
        c = self.cards[-1]
        self.remove_card(c)
        return c

    # Divides deck into num sub-decks and returns the list of sub-decks
    def divide(self, num):
        if self.cards == None:
            return
        decks = []
        quant = len(self.cards) // num
        rem = len(self.cards) % num
        i = 0
        for deck_ind in range(rem):
            decks.append(CardDeck(self.cards[i : i + quant + 1]))
            i += quant + 1
        for deck_ind in range(rem, num):
            decks.append(CardDeck(self.cards[i : i + quant]))
            i += quant
        return decks

    def add_card(self, card):
        if self.cards == None:
            self.cards = [card]
        else:
            self.cards += [card]

    # Remove a card when a player with a special ability does so
    def remove_card(self, card):
        if self.cards == None:
            return
        self.cards.remove(card)


class EventCard(object):

    # Government Grant: Build a research station in any city
    # One Quiet Night: Skip the "Infection" step
    # Forecast: Draw, observe, and rearrange top (6) infection cards
    # Airlift: Move any player to any city
    # Resilient Population: Remove any card in the infection discard pile from the game

    def __init__(self, card_value):
        self.value = card_value
        self.retrieved = False  #Dormant code - awaiting Contingency Planner implementation
        if self.value == "Government Grant":
            self.instruction = "Build a research station in any city"
            self.playfunc = "government_grant()"
        elif self.value == "One Quiet Night":
            self.instruction = "Skip the Infection step"
            self.playfunc = "one_quiet_night()"
        elif self.value == "Forecast":
            self.instruction = (
                "Draw, observe, and rearrange top (6) infection cards"
            )
            self.playfunc = "forecast()"
        elif self.value == "Airlift":
            self.instruction = "Move any player to any city"
            self.playfunc = "airlift()"
        elif self.value == "Resilient Population":
            self.instruction = (
                "Remove any card in the infection discard pile from the game"
            )
            self.playfunc = "resilient_population()"

    def play(self):
        return eval(self.playfunc)


class CityCard(object):

    def __init__(self, city):
        self.value = city.name
        self.retrieved = False  #Dormant code - awaiting expansion roles implementation
        self.city = city
        self.disease = city.default_disease


class EpidemicCard(object):
    def __init__(self):
        self.value = "Epidemic!"
        self.playfunc = "epidemic()"

    def play(self):
        eval(self.playfunc)


class InfectCard(object):

    # Only required for "Field Operative" Expansion Role
    #    retrieved = False

    def __init__(self, city):
        self.city = city
        self.value = city.name

    def play(self, outbreaks, quant=1):
        return self.city.infect(
            outbreaks, disease=self.city.default_disease, quantity=quant
        )

class City(object):
    def __init__(self, name, pop):
        self.name = name
        self.population = pop
        self.default_disease = None
        self.neighbors = []
        self.quarantine = {"Black": False, "Yellow": False, "Red": False, "Blue": False}
        self.diseases = {"Black": 0, "Yellow": 0, "Red": 0, "Blue": 0}
        self.pawns = []
        self.rs = False

    def gen_city_card(self):
        return CityCard(self)

    def gen_inf_card(self):
        return InfectCard(self)

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def move_from(self, plyr):
        self.pawns.remove(plyr)

    def move_to(self, plyr):
        self.pawns.append(plyr)

    def infect(self, outbreaks, disease="", quantity=1):
        if disease == "":
            disease = self.default_disease
        if self.quarantine[disease]:
            print("\n%s is under quarantine." %self.name)
            return outbreaks
        elif disease in eradicated:
            print(
                "\n%s is eradicated and will not infect %s" 
                  %(disease, self.name)
                  )
            return outbreaks
        print("\n%s (%s) has been infected with %i %s cube(s) [%s total]"
              %(self.name,
                self.default_disease, 
                quantity, 
                disease,
                self.diseases[disease]+quantity
                )
              )

        # May need to move this to game function in order to track outbreaks
        if self.diseases[disease] + quantity < CUBE_LIMIT + 1:
            self.diseases[disease] += quantity
            disease_cubes[disease] -= quantity
            print("%s disease cubes changes from %i to %i"  #Code smell: duplicate print statement with heal()
                  %(disease,
                    disease_cubes[disease] + quantity,
                    disease_cubes[disease])
                  )
        else:
            print("Outbreak in %s!" %self.name)
            self.diseases[disease] = CUBE_LIMIT
            outbreaks += 1
            self.quarantine[disease] = True
            for neighbor in self.neighbors:
                outbreaks = neighbor.infect(outbreaks, disease=disease)
            self.quarantine[disease] = False
        return outbreaks

    def heal(self, disease="", quantity=1):
        if disease == "":
            disease = self.default_disease
        self.diseases[disease] -= quantity
        disease_cubes[disease] += quantity
        print("%s disease cubes changes from %i to %i"  #Code smell: duplicate
              %(disease,
                disease_cubes[disease] - quantity,
                disease_cubes[disease])
              )

    #    def infect_neighbors(self, disease, quantity = 1):
    #        for neighbor in self.neighbors:
    #            neighbor.infect(disease)

    def build(self, research_stations):
        self.rs = True
        research_stations -= 1
        return research_stations

    #        return research_stations - 1

    def remove_rs(self, research_stations):
        self.rs = False
        research_stations += 1
        return research_stations


class Player(object):
    global cities
    def __init__(self,
                 player_name,
                 role,
                 actions = ACTIONS_PER_TURN,
                 cards = CARDS_TO_CURE,
                 max_cards = MAX_CARDS_IN_HAND):
        self.name = player_name
        self.role = role
        self.special_ability = roles[role]
        self.actions_per_turn = actions
        self.cards_to_cure = cards
        self.max_cards = max_cards
        self.cards = {}
        self.location = None

    def set_location(self, location):
        self.location = location

    def draw_card(self, deck):
        c = deck.draw_top()
        if c.value == "Epidemic!":
            print("Uh-oh")
        else:
            self.cards[c.value] = c
        return c

    def move(self, new_city_name):
        cities[self.location.name].move_from(self)
        self.location = cities[new_city_name]
        cities[new_city_name].move_to(self)

    #def assign_role(self, role):
    #    self.role = role
    #    self.special_ability = roles[role]

    def play_card(self, card_name):
        p_c = self.cards[card_name]
        played = True
        if type(self.cards[card_name]) is EventCard:
            played = self.cards[card_name].play()
        if not played:
            return None
        del self.cards[card_name]
        return p_c