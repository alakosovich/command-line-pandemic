# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 08:57:13 2021

@author: Alexander Lakocy
"""

from objects import City, Player
import random

def assign_roles(player_list, poss_roles):
    print("Assigning Roles...")
    players = {}
    for plyr_name in player_list:
        l = len(poss_roles)
        ind = random.randint(0, l - 1)
        r = poss_roles.pop(ind)
        if r == "Scientist":
            players[plyr_name] = Player(plyr_name, r, cards = 4)
        elif r == "Archivist":
            players[plyr_name] = Player(plyr_name, r, max_cards = 8)
        elif r == "Generalist":
            players[plyr_name] = Player(plyr_name, r, actions = 5)
        else:
            players[plyr_name] = Player(plyr_name, r)
    return players


def generate_cities(city_list):
    print("Generating Map...")
    cities = {}
    for city_name, city_pop in city_list:
        cities[city_name] = City(city_name, city_pop)
    return cities


def generate_neighbors(neighbor_list, cities):
    print("Populating Neighbors...")
    for cityA, cityB in neighbor_list:
        cities[cityA].add_neighbor(cities[cityB])
        cities[cityB].add_neighbor(cities[cityA])
    return cities


def assign_diseases(disease_dict, cities):
    print("Assigning Diseases...")
    for city_name in disease_dict:
        cities[city_name].default_disease = disease_dict[city_name]
    return cities