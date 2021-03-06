# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 08:42:17 2021

@author: Alexander Lakocy
"""


###############################################################################
# Player Utilities

command_list = [
    "list_actions()",
    "infection_status(city='all')",
    "player_status(p_name='')",
    "team_status()",
    "card_status()",
    "discarded_player_cards()",
    "discarded_infection_cards()",
    "locate_players()",
    "adjacent_cities(city=location)",
    "summary_status()",
    "detail_status()",
    "list_commands()",
]

def list_actions():
    print("\nActions available to active player:")
    print("\nPlay: Play Event Card from any player's hand "
          "(doesn't count as an action)"
          "\n'Play [card_name]'")
    print("\n'Move [player_name]* [city_name]' \t|| "
          "*[player_name] only used by Dispatcher")
    print("\nHeal: Remove disease cubes from current city"
          "\n'Heal [disease]*' \t|| "
          "*[disease] optional, reverts to default_disease]")
    print("\nShare Knowledge: Give city card to another player."
          "\nBoth players must be in the same city."
          "\nUnless giving player is 'Researcher', both players must be in "
          "the city matching the card being shared."
          "\n'Share [city_card_name] [player_name]'")
    print("\nTake Knowledge: Take city card from 'Researcher'"
          "\nActive player and 'Researcher' must be in the same city"
          "\n'Take [city_card_name]'")
    print("\nCure Disease: "
          "Turn in cards from active player's hand to cure a disease"
          "\n'Cure [disease]*' \t|| *[disease] optional")
    print("\nBuild Research Station: Requires city card matching current city"
          "\n'Build'")
    print("\nType 'list_commands()' for a summary of available information")

def infection_status(city="All"):
    if city != "All":
        try:
            c = cities[city]
        except:
            print("No city by the name of %s" %city)
            return
        print("%s: %s" 
              %(c.name, str([str(k) + ":" + str(v) for k, v in c.diseases]))
              )
    else:
        for disease in disease_list:
            print("\n%s:" %disease)
            for i in range(3, 0, -1):
                print("%i cubes:" %i)
                #                print([c.name+" \n" for c in cities.keys() if c.diseases[disease] == i])
                for c in cities.values():
                    if c.diseases[disease] == i:
                        print("     %s" %c.name)


def player_status(p_name=""):
    if p_name == "":
        p = current_player
    else:
        p = players[p_name]
    print("\nCurrent Player Status\n")
    print("Player: %s (%s)" %(p.name, p.role))
    print("Location: %s" %p.location.name)
    print("Player Cards: ")
    for c in p.cards.keys():
        try:
            print("%s (%s)" %(c, p.cards[c].disease))
        except:
            print("%s (%s)" %(c, p.cards[c].instruction))


def team_status():
    print("\nCurrent Game Status:\n")
    print("Outbreaks: %i/%i" %(outbreaks, MAX_OUTBREAKS))
    print("Cubes Remaining:\n")
    for disease in disease_list:
        print("%s: %i/%i" %(disease, disease_cubes[disease], QTY_CUBES))
    print("Player cards remaining: %i (%i/%i epidemics remaining)"
          %(len(player_deck.cards), num_epidemics,epidemics[difficulty])
    )
    print("Infection rate: %i cities per turn" %infection_rate)
    print("Diseases cured: %i/%i (%i eradicated)"
          %(len(cured), len(disease_list), len(eradicated))
    )
    print("Current Player: %s (%s)"
          %(current_player.name, current_player.role)
    )


def card_status():
    for player_name in player_list:
        print("\nPlayer %s (%s - %s)"
              %(player_name, 
                players[player_name].role,
                players[player_name].location.name
                )
        )
        for crd in players[player_name].cards.values():
            try:
                print("%s (%s)" %(crd.value, crd.disease))
            except:
                print("%s (%s)" %(crd.value, crd.instruction))


def discarded_player_cards():
    for crd in player_discard:
        try:
            print("%s (%s)" %(crd.value, crd.disease))
        except:
            try:
                print("%s: %s" %(crd.value, crd.instruction))
            except:
                print(crd.value)


def discarded_infection_cards():
    for crd in infect_discard:
        print("%s (%s)" %(crd.value, crd.disease))


def locate_players():
    for plyr_name in player_list:
        print(
            "Player %s (%s): %s" 
            %(plyr_name, 
              players[plyr_name].role, 
              players[plyr_name].location.name
              )
        )

def adjacent_cities():
    return
# city=current_player.location):
#    print("Current city: %s" %city.name)
#    print("Neighbors:")
#    print(["%s/n" %n for n in city.neighbors])

def list_commands():
    for command in command_list:
        print(command)


def summary_status():
    team_status()
    player_status()


def detail_status():
    infection_status()
    card_status()
    team_status()
    player_status()