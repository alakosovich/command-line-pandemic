# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 20:45:02 2018

@author: alakocy
"""

import random

# Dictionary [key = city_name] of city objects
global cities

# Card decks
global player_deck
global player_discard
global infect_deck
global infect_discard

# Game variables
# Number of epidemic cards remaining in player deck
global num_epidemics

# List of available roles
global poss_roles

# Number of remaining research station tokens
global research_stations

# List of cities with research stations
global rs_list

# Pointer to active_player
global active_player
global current_player
global player_list
global player_ind

# Dictionary identifying game cubes remaining for each disease
global disease_cubes

# Number of outbreaks that have occurred
global outbreaks

# Boolean - whether "Infect Cities" step will occur this turn
global infect_cities

# List of progressively higher infection rates
global infection_rates

# Number of infection cards drawn at the end of each turn
global infection_rate

# List of diseases that have been cured/eradicated
global cured
global eradicated

# List of player status commands
global command_list


# Assign Game Variables
active_player = None
current_player = None
infect_cities = True

disease_list = ["Blue", "Yellow", "Black", "Red"]

disease_cubes = {}
for disease in disease_list:
    disease_cubes[disease] = 24

outbreaks = 0

infection_rates = [2, 2, 2, 3, 3, 4, 4]
infection_rate = infection_rates.pop(0)

cured = []
eradicated = []


class card_deck(object):
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
            decks.append(card_deck(self.cards[i : i + quant + 1]))
            i += quant + 1
        for deck_ind in range(rem, num):
            decks.append(card_deck(self.cards[i : i + quant]))
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


class event_card(object):

    # Government Grant: Build a research station in any city
    # One Quiet Night: Skip the "Infection" step
    # Forecast: Draw, observe, and rearrange top (6) infection cards
    # Airlift: Move any player to any city
    # Resilient Population: Remove any card in the infection discard pile from the game

    retrieved = False

    def __init__(self, card_value):
        self.value = card_value
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
        return getattr(self, self.playfunc)


class city_card(object):

    # Only required for "Contingency Planner" Role
    retrieved = False

    def __init__(self, city):
        self.value = city.name
        self.city = city
        self.disease = city.default_disease


class epidemic_card(object):
    def __init__(self):
        self.value = "Epidemic!"
        self.playfunc = "epidemic()"

    def play(self):
        getattr(self, self.playfunc)


class infect_card(object):

    # Only required for "Field Operative" Expansion Role
    #    retrieved = False

    def __init__(self, city):
        self.city = city
        self.value = city.name

    def play(self, outbreaks, quant=1):
        return self.city.infect(
            outbreaks, disease=self.city.default_disease, quantity=quant
        )


class city(object):
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
        return city_card(self)

    def gen_inf_card(self):
        return infect_card(self)

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def infect(self, outbreaks, disease="", quantity=1):
        if disease == "":
            disease = self.default_disease
        if self.quarantine[disease]:
            print(self.name + " is under quarantine.")
            return outbreaks
        elif disease in eradicated:
            print(disease + " is eradicated and will not infect " + self.name)
            return outbreaks
        print(
            self.name
            + " ("
            + self.default_disease
            + ") has been infected with "
            + str(quantity)
            + " "
            + disease
            + " cube(s) ["
            + str(self.diseases[disease] + quantity)
            + " total]"
        )

        # May need to move this to game function in order to track outbreaks
        if self.diseases[disease] + quantity < 4:
            self.diseases[disease] += quantity
            disease_cubes[disease] -= quantity
            print(
                disease
                + " disease cubes changes from "
                + str(disease_cubes[disease] + quantity)
                + " to "
                + str(disease_cubes[disease])
            )
        else:
            print("Outbreak in " + self.name + "!")
            self.diseases[disease] = 3
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
        print(
            disease
            + " disease cubes changes from "
            + str(disease_cubes[disease] - quantity)
            + " to "
            + str(disease_cubes[disease])
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


class player(object):
    def __init__(self, player_name):
        self.name = player_name
        self.role = None
        self.cards = {}
        self.location = cities["Atlanta"]

    def draw_card(self, deck):
        c = deck.draw_top()
        if c.value == "Epidemic!":
            print("Uh-oh")
        else:
            self.cards[c.value] = c
        return c

    def move(self, new_city_name):
        cities[self.location.name].pawns.remove(self)
        self.location = cities[new_city_name]
        cities[new_city_name].pawns.append(self)

    def assign_role(self, role):
        self.role = role

    def play_card(self, card_name):
        p_c = self.cards[card_name]
        played = True
        if type(self.cards[card_name]) is event_card:
            played = self.cards[card_name].play()
        if not played:
            return None
        del self.cards[card_name]
        return p_c

    # Roles:
    # Scientist: XNeed only (4) city cards of the same color to discover cure
    # Researcher: XAs an action, may give (or another player may take) any city card from player's hand. Both players must be in the same city.
    # Medic: XRemove all cubes of one color when treating disease
    #       Automatically (no action required) remove cubes of cured diseases from the city player occupies (and prevent from being placed there)
    # Quarantine Specialist: Prevent infecting city player is in and all adjacent cities
    # Operations Expert: XAs an action, may construct research stations in current city without using the city card
    #                   Once per turn, as an action, may fly from a city with a research station to any city by discarding any city card
    # Contingency Planner: As an action, may retrieve discarded event card.  Retrieved card does not apply to hand count.  After playing retrieved card, remove from the game.
    # Dispatcher: XMay move another player as if your own
    #            As an action, may move any player to a city with another player

    # Expansion Roles???:
    # Field Operative: Once per turn, as an action, may move (1) cube from current city to role card
    #                 May cure a disease using (3) city cards plus (3) matching cubes from role card
    # Archivist: May keep up to (8) cards in hand at a time
    #           Once per turn, as an action, may retrieve discarded city card corresponding to player's current city
    # Generalist: May do up to (5) actions each turn
    # Epidemiologist: Once during player's turn, may take any city card from another player in the same city
    # Troubleshooter: May view as many upcoming infection cards as the current infection rate
    #                Once per turn, as an action, may fly to a city for which the player owns the city card without discarding the card


###############################################################################
# Game Setup


def assign_roles(player_list):
    print("Assigning Roles...")
    global players
    global poss_roles
    players = {}
    for plyr in player_list:
        players[plyr] = player(plyr)
        l = len(poss_roles)
        ind = random.randint(0, l - 1)
        players[plyr].role = poss_roles.pop(ind)
    return


def generate_cities(city_list):
    print("Generating Map...")
    global cities
    cities = {}
    for city_name, city_pop in city_list:
        cities[city_name] = city(city_name, city_pop)
    return


def generate_neighbors(neighbor_list):
    print("Populating Neighbors...")
    for cityA, cityB in neighbor_list:
        cities[cityA].add_neighbor(cities[cityB])
        cities[cityB].add_neighbor(cities[cityA])
    return


def assign_diseases(disease_dict):
    print("Assigning Diseases...")
    for city_name in disease_dict:
        cities[city_name].default_disease = disease_dict[city_name]
    return


neighbor_pairs = []
pairwise_dict = {
    "New York": ["London", "Madrid", "Washington", "Montreal"],
    "Montreal": ["Chicago", "Washington"],
    "Washington": ["Miami", "Atlanta"],
    "Chicago": ["San Francisco", "Los Angeles", "Atlanta", "Mexico City"],
    "San Francisco": ["Los Angeles", "Tokyo", "Manila"],
    "Mexico City": ["Los Angeles", "Lima", "Bogota", "Miami"],
    "Miami": ["Bogota", "Atlanta"],
    "Bogota": ["Lima", "Buenos Aires", "Sao Paulo"],
    "Lima": ["Santiago"],
    "Sao Paulo": ["Madrid", "Lagos", "Buenos Aires"],
    "Lagos": ["Kinshasha", "Khartoum"],
    "Kinshasha": ["Khartoum", "Johannesburg"],
    "Khartoum": ["Johannesburg", "Cairo"],
    "Cairo": ["Riyadh", "Baghdad", "Istanbul", "Algiers"],
    "Algiers": ["Madrid", "Paris", "Istanbul"],
    "Madrid": ["London", "Paris"],
    "Paris": ["London", "Essen", "Milan"],
    "Essen": ["London", "Milan", "St. Petersburg"],
    "St. Petersburg": ["Moscow", "Istanbul"],
    "Moscow": ["Istanbul", "Tehran"],
    "Istanbul": ["Baghdad", "Milan"],
    "Tehran": ["Baghdad", "Karachi", "Delhi"],
    "Riyadh": ["Baghdad", "Karachi"],
    "Karachi": ["Baghdad"],
    "Delhi": ["Kolkata", "Chennai", "Mumbai", "Karachi"],
    "Kolkata": ["Chennai", "Bangkok", "Hong Kong"],
    "Mumbai": ["Chennai", "Karachi"],
    "Bangkok": ["Ho Chi Minh City", "Hong Kong", "Jakarta", "Chennai"],
    "Jakarta": ["Sydney", "Ho Chi Minh City", "Chennai"],
    "Manila": ["Ho Chi Minh City", "Taipei", "Hong Kong", "Sydney"],
    "Sydney": ["Los Angeles"],
    "Hong Kong": ["Ho Chi Minh City", "Taipei", "Shanghai"],
    "Taipei": ["Osaka", "Shanghai"],
    "Shanghai": ["Beijing", "Seoul", "Tokyo"],
    "Tokyo": ["Osaka", "Seoul"],
    "Seoul": ["Beijing"],
}

# city_pool = [x"New York","Atlanta",x"Chicago",x"Montreal",x"Washington",x"San Francisco",
# "Los Angeles",x"Miami",x"Mexico City","Bogota","Lima","Santiago","Buenos Aires","Sao Paulo","Lagos","Kinshasha","Johannesburg","Khartoum", "St. Petersburg","Madrid","London","Essen","Paris","Milan",
# "Cairo","Algiers","Istanbul","Moscow","Tehran","Baghdad","Riyadh","Karachi","Delhi","Mumbai","Chennai","Kolkata",
# "Bangkok","Jakarta","Sydney","Manila","Ho Chi Minh City","Hong Kong","Taipei","Osaka","Tokyo","Seoul","Beijing","Shanghai"]

city_data = [
    ("New York", 8537673, "Blue"),
    ("Atlanta", 472522, "Blue"),
    ("Montreal", 1704694, "Blue"),
    ("Washington", 693972, "Blue"),
    ("San Francisco", 870887, "Blue"),
    ("Chicago", 2705000, "Blue"),
    ("Essen", 50000, "Blue"),
    ("Paris", 2206488, "Blue"),
    ("London", 8788000, "Blue"),
    ("Milan", 1331000, "Blue"),
    ("St. Petersburg", 260999, "Blue"),
    ("Madrid", 3166000, "Blue"),
    ("Karachi", 400000, "Black"),
    ("Moscow", 11920000, "Black"),
    ("Tehran", 8154000, "Black"),
    ("Baghdad", 7665000, "Black"),
    ("Riyadh", 5188000, "Black"),
    ("Delhi", 18980000, "Black"),
    ("Chennai", 7088000, "Black"),
    ("Cairo", 9500000, "Black"),
    ("Algiers", 2713000, "Black"),
    ("Istanbul", 14800000, "Black"),
    ("Mumbai", 18410000, "Black"),
    ("Miami", 453579, "Yellow"),
    ("Mexico City", 8851000, "Yellow"),
    ("Los Angeles", 3976322, "Yellow"),
    ("Lagos", 21500000, "Yellow"),
    ("Bogota", 8081000, "Yellow"),
    ("Santiago", 69018, "Yellow"),
    ("Lima", 9752000, "Yellow"),
    ("Buenos Aires", 2891000, "Yellow"),
    ("Sao Paulo", 12040000, "Yellow"),
    ("Kinshasha", 9464000, "Yellow"),
    ("Johannesburg", 957441, "Yellow"),
    ("Khartoum", 5185000, "Yellow"),
    ("Manila", 1780000, "Red"),
    ("Ho Chi Minh City", 8426000, "Red"),
    ("Hong Kong", 7347000, "Red"),
    ("Seoul", 9860000, "Red"),
    ("Sydney", 5029768, "Red"),
    ("Taipei", 2704810, "Red"),
    ("Osaka", 2691000, "Red"),
    ("Tokyo", 9273000, "Red"),
    ("Beijing", 21500000, "Red"),
    ("Shanghai", 24150000, "Red"),
    ("Jakarta", 10075310, "Red"),
    ("Kolkata", 4497000, "Black"),
    ("Bangkok", 8281000, "Red"),
]

for cityA in pairwise_dict.keys():
    for cityB in pairwise_dict[cityA]:
        neighbor_pairs.append((cityA, cityB))

city_info_list = []

for (c, p, d) in city_data:
    city_info_list.append((c, p))

generate_cities(city_info_list)

generate_neighbors(neighbor_pairs)

disease_dict = {}

for (c, p, d) in city_data:
    disease_dict[c] = d

# disease_dict = {"New York":"Blue","Montreal":"Blue","Washington":"Blue","Chicago":"Blue",
#                "Atlanta":"Yellow","Miami":"Yellow","Mexico City":"Yellow","Los Angeles":"Yellow",
#                "San Francisco":"Red"}

assign_diseases(disease_dict)

# for nghbr in cities["New York"].neighbors:
#    print(nghbr.name)
#
# for nghbr in cities["Atlanta"].neighbors:
#    print(nghbr.name)


# for i in range(epidemics[difficulty]):
#    player_cards.append(epidemic_card())
#
# player_deck = card_deck(player_cards)

###############################################################################
# Game Operation

# When "Epidemic" card is drawn
def epidemic():
    global infection_rate
    global infect_deck
    global infect_discard
    global num_epidemics
    global outbreaks

    # 1: Increase infection rate marker
    infection_rate = infection_rates.pop(0)

    # 2: Infect "new" city
    inf_card = infect_deck.draw_bot()
    outbreaks = cities[inf_card.value].infect(outbreaks, quantity=3)
    infect_discard.add_card(inf_card)

    # Option for any player to use "Resilient Population" event card
    has_rp_card = False
    plyr_who_has = None
    for plyr_name in player_list:
        if "Resilient Population" in [
            crd.value for crd in players[plyr_name].cards.values()
        ]:
            has_rp_card = True
            plyr_who_has = plyr_name
            break
    if has_rp_card:
        print("Enter 'Y' to play 'Resilient Population' event card:")
        dec = input().strip()
        if dec == "Y" or dec == "y":
            players[plyr_who_has].play_card("Resilient Population")

    # 3: Intensify (shuffle infect_discard + place on top of infect_deck)
    infect_discard.shuffle()
    infect_deck = combine([infect_discard, infect_deck])
    infect_discard = card_deck(None)

    num_epidemics -= 1


# Combines multiple sub-decks (by stacking, no shuffling) and returns the combination
def combine(deck_list):
    card_list = []
    for sub in deck_list:
        card_list += sub.cards
    return card_deck(card_list)


###############################################################################
###############################################################################
# Game Board Setup

###############################################################################
# User input:
while True:
    print("Enter Number of Players(1-4):")
    try:
        num_players = int(input().strip())
    except:
        print("Number not recognized.")
        continue
    if num_players > 0 and num_players < 5:
        break
    else:
        print("Number of players must be between 1 and 4")


player_list = []

for i in range(1, num_players + 1):
    print("Enter Player " + str(i) + " Name:")
    player_list.append(input().strip())

print("Enter Difficulty (Easy, Intermediate, Hard):")
difficulty = input().strip()

# print("Enter Player List:")


# num_players = 4
# player_list = ["Big Al","Bigger Al","Lazy Susan","Debbie Downer"]
# difficulty = "Intermediate"

###############################################################################
# Card Decks:


research_stations = 6

research_stations = cities["Atlanta"].build(research_stations)

print("Constructing Card Decks...")

epidemics = {"Easy": 4, "Intermediate": 5, "Hard": 6}
num_epidemics = epidemics[difficulty]

event_card_list = [
    "Government Grant",
    "One Quiet Night",
    "Forecast",
    "Airlift",
    "Resilient Population",
]
poss_roles = [
    "Scientist",
    "Researcher",
    "Quarantine Specialist",
    "Medic",
    "Dispatcher",
    "Operations Expert",
]  # "Contingency Planner", #(not setup yet)

assign_roles(player_list)

player_cards = []
infect_cards = []

for city_obj in cities.values():
    player_cards.append(city_obj.gen_city_card())
    infect_cards.append(city_obj.gen_inf_card())

for e_card in event_card_list:
    player_cards.append(event_card(e_card))

player_deck = card_deck(player_cards)
player_deck.shuffle()

# Draw city cards before placing "Epidemic" cards in deck
num_start_cards = 6 - num_players
for p in players:
    for i in range(num_start_cards):
        players[p].draw_card(player_deck)
    cities["Atlanta"].pawns.append(players[p])

# Divide player deck into equal sub-decks to distribute "Epidemic" cards
sub_decks = player_deck.divide(num_epidemics)

# Add one "Epidemic" card to each sub-deck, then shuffle sub-deck
for sub in sub_decks:
    a = epidemic_card()
    sub.add_card(a)
    sub.shuffle()

player_deck = combine(sub_decks)

infect_deck = card_deck(infect_cards)
infect_deck.shuffle()

# Create empty decks for discard piles
player_discard = card_deck(None)
infect_discard = card_deck(None)

# print("\nAfter:")
# print("Player Cards:__________________")
# for j in player_deck.cards:
#    print(j.value)
#
# print("Infect Cards:__________________")
# for k in infect_deck.cards:
#    print(k.value)

##"test" sorting algorithm
# trial_list = [i for i in range(20)]
# trial_deck = card_deck(trial_list)
# trial_deck.shuffle()
# print([card for card in trial_deck.cards])

###############################################################################
# Initial Infections

print("Roles have been assigned:")
for p in players:
    print(players[p].name + ": " + players[p].role)

print("Cities will now be infected")

# Infect (3) cities with 3 disease cubes, (3) with 2 cubes, (3) with 1 cube
for n_cubes in range(3, 0, -1):
    for j in range(3):
        current_inf = infect_deck.draw_top()
        cities[current_inf.value].infect(outbreaks, quantity=n_cubes)
        infect_discard.add_card(current_inf)


###############################################################################
# Game Variables

max_pop = 0
max_city = None
max_player = None
for p in players:
    for cur_card in players[p].cards.keys():
        try:
            c = players[p].cards[cur_card].city
        except:
            continue
        if c.population > max_pop:
            max_pop = c.population
            max_city = c
            max_player = players[p]

print(
    "Player '"
    + max_player.name
    + "' has the highest population city card ("
    + max_city.name
    + ", "
    + str(max_pop)
    + ")"
)
print("Player '" + max_player.name + "' will go first")

active_player = max_player
player_ind = player_list.index(active_player.name)


###############################################################################
# Player Utilities

command_list = [
    "infection_status(city='all')",
    "player_status()",
    "team_status()",
    "card_status()",
    "discarded_player_cards()",
    "discarded_infection_cards()",
    "locate_players()",
    "adjacent_cities(city=location)",
    "list_commands()",
]


def infection_status(city="All"):
    if city != "All":
        try:
            c = cities[city]
        except:
            print("No city by the name of " + city)
            return
        print(c.name + ": " + str([str(k) + ":" + str(v) for k, v in c.diseases]))
    else:
        for disease in disease_list:
            print("\n" + disease + ":")
            for i in range(3, 0, -1):
                print(str(i) + " cubes:")
                #                print([c.name+" \n" for c in cities.keys() if c.diseases[disease] == i])
                for c in cities.values():
                    if c.diseases[disease] == i:
                        print("    " + c.name)


def player_status(p_name=""):
    if p_name == "":
        p = current_player
    else:
        p = players[p_name]
    print("\nCurrent Player Status\n")
    print("Player: " + p.name + " (" + p.role + ")")
    print("Location: " + p.location.name)
    print("Player Cards: ")
    for c in p.cards.keys():
        try:
            print(c + " (" + p.cards[c].disease + ")")
        except:
            print(c + " (" + p.cards[c].instruction + ")")


def team_status():
    print("\nCurrent Game Status:\n")
    print("Outbreaks: " + str(outbreaks) + "/8")
    print("Cubes Remaining:\n")
    for disease in disease_list:
        print(disease + ": " + str(disease_cubes[disease]) + "/24")
    print(
        "Player cards remaining: "
        + str(len(player_deck.cards))
        + " ("
        + str(num_epidemics)
        + "/"
        + str(epidemics[difficulty])
        + " epidemics remaining)"
    )
    print("Infection rate: " + str(infection_rate) + " cities per turn")
    print(
        "Diseases cured: "
        + str(len(cured))
        + "/"
        + str(len(disease_list))
        + " ("
        + str(len(eradicated))
        + " eradicated)"
    )
    print("Current Player: " + current_player.name + " (" + current_player.role + ")")


def card_status():
    for player_name in player_list:
        print(
            "\nPlayer "
            + player_name
            + " ("
            + players[player_name].role
            + " - "
            + players[player_name].location.name
            + ")"
        )
        for crd in players[player_name].cards.values():
            try:
                print(crd.value + " (" + crd.disease + ")")
            except:
                print(crd.value + ": " + crd.instruction)


def discarded_player_cards():
    for crd in player_discard:
        try:
            print(crd.value + " (" + crd.disease + ")")
        except:
            try:
                print(crd.value + ": " + crd.instruction)
            except:
                print(crd.value)


def discarded_infection_cards():
    for crd in infect_discard:
        print(crd.value + " (" + crd.disease + ")")


def locate_players():
    for plyr_name in player_list:
        print(
            "Player "
            + plyr_name
            + " ("
            + players[plyr_name].role
            + "): "
            + players[plyr_name].location.name
        )


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


###############################################################################
###############################################################################
# Gameplay

###############################################################################
# Internal Functions

# Check win condition
def check_win():
    global cured
    global disease_list

    if len(cured) == len(disease_list):
        print(
            "All diseases have been cured.  Pandemic has been contained.\nEnter 'Continue' to keep playing:"
        )
        cmd = input().strip()
        if not "continue" in cmd.lower():
            return False
        return True


def impose_quarantine():
    return


def card_limit(player_name):
    global players
    global cities
    global player_discard

    while len(players[player_name].cards.keys()) > 7:
        print(
            "Player %s has %s cards in hand (7 allowed)"
            % (player_name, str(len(players[player_name].cards.keys())))
        )
        #     "Player "
        #     + player_name
        #     + " has "
        #     + str(len(players[player_name].cards.keys()))
        #     + " cards in hand (7 allowed):"
        # )
        for c in players[player_name].cards.keys():
            try:
                print(c + " (" + players[player_name].cards[c].disease + ")")
            except:
                print(c + " (" + players[player_name].cards[c].instruction + ")")
        print("Enter city card to discard or event card to play.")
        crd = input().strip()

        try:
            crd_played = players[player_name].play_card(crd)
            player_discard.add_card(crd_played)

        except:
            print("Card value not recognized.")
            continue
    return


# Check whether any cured diseases have been eradicated
def check_eradicated():
    global cured
    global eradicated
    global disease_cubes

    for dis in cured:
        if dis in eradicated:
            continue
        if disease_cubes[dis] == 24:
            eradicated.append(dis)
            print("%s has been eradicated" % dis)


# Check Medic 2nd ability
def medic_auto_heal():
    global players
    global cities
    global cured
    global eradicated
    global disease_cubes

    for plyr_name in players.keys():
        if players[plyr_name].role == "Medic":
            cur_city_name = players[plyr_name].location.name
            for d in cured:
                if cities[cur_city_name].diseases[d] > 0:
                    print(
                        "Medic has healed "
                        + str(cities[cur_city_name].diseases[d])
                        + " "
                        + d
                        + " cubes from "
                        + cur_city_name
                        + " automatically."
                    )
                    cities[cur_city_name].heal(
                        disease=d, quantity=cities[cur_city_name].diseases[d]
                    )
                    check_eradicated()
    #                    if disease_cubes[d] == 24:
    #                        eradicated.append(d)
    #                        print(d+" has been eradicated")
    return


###############################################################################
# Event Card Functions


def government_grant():
    global research_stations
    print("Enter city to build research station in:")
    city_name = input().strip()
    if city_name == "Stop" or city_name == "stop":
        print("Action card cancelled.")
        return False
    try:
        assert cities[city_name].rs == False
        city_name

        if research_stations == 0:
            print(
                "No available research stations.  Enter city to remove research station from first."
            )
            com = input().strip()
            try:
                research_stations = cities[com].remove_rs(research_stations)
            except:
                print("City name not recognized.  Cancel building research station")
                return False

        research_stations = cities[city_name].build(research_stations)
    except:
        print("Unable to build research station.")
        return False
    return True


def one_quiet_night():
    global infect_cities
    print("One Quiet Night card will be played.  Enter 'Stop' to cancel.")
    stop = input().strip()
    if stop == "Stop" or stop == "stop":
        print("Action card cancelled.")
        return False

    infect_cities = False
    return True


def forecast():
    global infect_deck
    top_6_list = []
    infection_status()
    print("\n")
    print("Top 6 cards are:")
    for c_ind in range(6):
        crd = infect_deck.draw_top()
        print(crd.value + " (" + crd.city.default_disease + ")")
        top_6_list.append(crd)

    new_6_list = []
    c_new_ind = 1
    while c_new_ind in range(1, 7):
        print("Enter card for position " + str(c_new_ind) + " (1 will be drawn next)")
        c_val = input().strip()
        if c_val == "Stop" or c_val == "stop":
            infect_deck = combine([card_deck(top_6_list), infect_deck])
            return False
        for crd in top_6_list:
            if crd.value == c_val:
                new_6_list.append(crd)
                break
        if len(new_6_list) == c_new_ind:
            c_new_ind += 1
        else:
            print("Card value not recognized.")
    infect_deck = combine([card_deck(new_6_list), infect_deck])
    return True


def airlift():
    print("Enter player to airlift:")
    player_name = input().strip()
    print("Enter destination city:")
    dest_city_name = input().strip()
    if (player_name == "Stop" or player_name == "stop") or (
        dest_city_name == "Stop" or dest_city_name == "stop"
    ):
        print("Action card cancelled.")
        return False

    try:
        assert players[player_name].location.name != dest_city_name
        players[player_name].move(dest_city_name)

    except:
        print("Unable to airlift " + player_name + " to " + dest_city_name)
        return False

    # Medic 2nd ability
    medic_auto_heal()

    return True


def resilient_population():
    print("Resilient Population")
    print("Current infection discard pile:")
    global infect_discard
    for crd in infect_discard.cards:
        print(crd.value + " (" + crd.city.default_disease + ")")

    print("Enter infection card to remove from game:")
    crd_value = input().strip()
    if crd_value == "Stop" or crd_value == "stop":
        print("Action card cancelled.")
        return False
    try:
        crd_ptr_ind = [crd.value for crd in infect_discard.cards].index(crd_value)
        infect_discard.remove_card(infect_discard.cards[crd_ptr_ind])
    except:
        print("Card not found.")
        return False
    return True


###############################################################################
# Actions

# action function is called each time actions remain for a player's turn
# action returns number of successfully completed actions
def action(i):
    global players
    global cities
    global current_player
    global player_discard
    global disease_cubes

    # Medic 2nd ability at start of action
    medic_auto_heal()

    # Play Card
    def play(command):
        try:
            space_ind = command.index(" ")
            event_card_value = command[space_ind + 1 :]
            owner_name = ""
            for plyr in player_list:
                if event_card_value in players[plyr].cards.keys():
                    owner_name = plyr
                    break
            if owner_name == "":
                print("Card not found in any player's hand.")
                return 0
        except:
            print("Event card value not recognized.")
            return 0
        crd = players[owner_name].play_card(event_card_value)
        try:
            assert event_card_value not in players[owner_name].cards.keys()
            player_discard.add_card(crd)
            return 0
        except:
            print("Fail :(")

        # playing an event card does not require any actions
        return 0

    # Move Pawn
    def move(command):
        global active_player
        global current_player

        if current_player.role == "Dispatcher":
            try:
                space_ind = command.index(" ")
                rem_cmd = command[space_ind + 1 :]
                found = False
                for plyr_name in players.keys():
                    if plyr_name in rem_cmd[: len(plyr_name)]:
                        dest_city_name = rem_cmd[
                            rem_cmd.index(plyr_name) + len(plyr_name) + 1 :
                        ]
                        if dest_city_name not in cities.keys():
                            continue
                        else:
                            found = True
                            active_player = players[plyr_name]
                            print(
                                "Current player is 'Dispatcher'.  Move player '"
                                + plyr_name
                                + "' to "
                                + dest_city_name
                            )
                            break
                if not found:
                    raise Exception
            except:
                print("Current player is 'Dispatcher'. Enter player to move:")
                act_plyr_name = input().strip()
                try:
                    active_player = players[act_plyr_name]
                    print("Active player is " + act_plyr_name)

                except:
                    print(
                        "Player name not recognized. Defaulting to "
                        + current_player.name
                    )
                    active_player = players[current_player.name]
                print("Enter destination city:")
                dest_city_name = input().strip()

        else:
            try:
                space_ind = command.index(" ")
                dest_city_name = command[space_ind + 1 :]
            except:
                print("Command name not recognized.")
                return 0
        try:
            dest_city = cities[dest_city_name]
        except:
            print("Command name not recognized.")
            return 0

        # Drive/Ferry (1 move) - must be to an adjacent city
        if dest_city in cities[active_player.location.name].neighbors:
            print(
                "Drive/Ferry from "
                + active_player.location.name
                + " to "
                + dest_city.name
            )
            active_player.move(dest_city.name)

        #            #Medic 2nd ability
        #            #ADD SEPARATE FUNCTION (& RELOCATE CALL TO END OF 'MOVE' FUNCTION??)
        #            ###################################################################
        #            if active_player.role == "Medic":
        #                for d in cured:
        #                    dest_city.diseases[d] = 0
        #            return 1

        # Shuttle Flight (1 move) - must be research station in both cities
        elif active_player.location.rs and dest_city.rs:
            print(
                "Shuttle Flight from "
                + active_player.location.name
                + " to "
                + dest_city.name
            )
            active_player.move(dest_city.name)

        #            #Medic 2nd ability
        #            #ADD SEPARATE FUNCTION (& RELOCATE CALL TO END OF 'MOVE' FUNCTION??)
        #            ###################################################################
        #            if active_player.role == "Medic":
        #                for d in cured:
        #                    print("Medic has cured "+d+" from "+dest_city+" automatically")
        #                    dest_city.heal(disease = d, quantity = dest_city.diseases[d])
        #            return 1

        # Dispatcher ability: Move any pawn (active) to any city with another pawn
        elif current_player.role == "Dispatcher" and len(dest_city.pawns) > 0:
            print(
                "Dispatcher sends "
                + active_player.name
                + " from "
                + active_player.location.name
                + " to "
                + dest_city.name
            )
            active_player.move(dest_city.name)

        #            #Medic 2nd ability
        #            if active_player.role == "Medic":
        #                for d in cured:
        #                    print("Medic has cured "+d+" from "+dest_city+" automatically")
        #                    dest_city.heal(disease = d, quantity = dest_city.diseases[d])
        #            return 1

        # Direct Flight or Charter Flight (1 move)
        else:

            try:

                # Direct Flight - player has destination city card
                if dest_city.name in current_player.cards.keys():
                    print(
                        "Direct Flight to "
                        + dest_city.name
                        + " requires discarding player card.  Y to confirm"
                    )
                    con = input().strip()
                    if con.lower() == "y":
                        active_player.move(dest_city.name)
                        crd = current_player.play_card(dest_city.name)
                        player_discard.add_card(crd)

                        #                        #Medic 2nd ability
                        #                        if active_player.role == "Medic":
                        #                            for d in cured:
                        #                                print("Medic has cured "+d+" from "+dest_city+" automatically")
                        #                                dest_city.heal(disease = d, quantity = dest_city.diseases[d])

                        medic_auto_heal()

                        return 1

                # Charter Flight - player has origin city card
                if active_player.location.name in current_player.cards.keys():
                    print(
                        "Charter Flight to "
                        + dest_city.name
                        + " requires discarding "
                        + active_player.location.name
                        + " player card.  Y to confirm"
                    )
                    con = input().strip()
                    if con.lower() == "y":
                        origin_city_name = active_player.location.name
                        active_player.move(dest_city.name)
                        crd = current_player.play_card(origin_city_name)
                        player_discard.add_card(crd)

                    else:
                        print("Move cancelled")
                        return 0

                #                        #Medic 2nd ability
                #                        if active_player.role == "Medic":
                #                            for d in cured:
                #                                print("Medic has cured "+d+" from "+dest_city+" automatically")
                #                                dest_city.heal(disease = d, quantity = dest_city.diseases[d])
                # Operations Expert 2nd ability - from a research station, may move to any other city by discarding any city card
                elif (
                    current_player.role == "Operations Expert"
                    and current_player.location.rs
                ):
                    print(
                        "Operations Expert may discard any card to fly from the "
                        + current_player.location.name
                        + " research station to "
                        + dest_city.name
                        + "."
                    )
                    print("Player cards:")
                    for c_name in current_player.cards.keys():
                        if type(current_player.cards[c_name]) is city_card:
                            print(c_name + " (" + cities[c_name].default_disease + ")")
                    print("Enter card to discard, or anything else to cancel.")
                    crd_name = input().strip()
                    try:
                        current_player.move(dest_city.name)
                        crd = current_player.play_card(crd_name)
                        player_discard.add_card(crd)
                    except:
                        print("City name not recognized, move cancelled.")
                        return 0

                else:
                    print("No available moves detected.")
                    return 0
            except:
                print("No available moves detected")
                return 0

        medic_auto_heal()
        #        #Medic 2nd ability
        #        if active_player.role == "Medic":
        #            for d in cured:
        #                print("Medic has cured "+d+" from "+dest_city+" automatically")
        #                dest_city.heal(disease = d, quantity = dest_city.diseases[d])
        return 1

    # Build Research Station
    def build(command):
        global players
        global cities
        global current_player
        global research_stations
        global player_discard

        if current_player.location.rs:
            print("Already a research station in " + current_player.location.name)
            return 0

        bld = False
        crd_reqd = True

        if current_player.role == "Operations Expert":
            bld = True
            crd_reqd = False
            print(
                "Build research station in "
                + current_player.location.name
                + " does not require a card."
            )
        elif active_player.location.name in current_player.cards.keys():
            bld = True
            print(
                "Build research station in "
                + current_player.location.name
                + " requires discarding player card."
            )
        try:
            assert bld
            print("Enter Y to confirm")
            con = input().strip()
            if con.lower() == "y":
                if research_stations == 0:
                    print(
                        "No available research stations.  Enter city to remove research station from first."
                    )
                    cty_name = input().strip()
                    try:
                        research_stations = cities[cty_name].remove_rs(
                            research_stations
                        )
                    except:
                        print(
                            "City name not recognized.  Cancel building research station"
                        )
                        return 0
                if crd_reqd:
                    crd = current_player.play_card(current_player.location.name)
                    player_discard.add_card(crd)
                research_stations = cities[current_player.location.name].build(
                    research_stations
                )
            return 1
        except:
            print("Unable to build research station.")
            return 0

    # Cure Disease
    def cure(command):
        global current_player
        global cured

        # Confirm city has a research station
        if not current_player.location.rs:
            print("Player must be in a city with a research station.")
            return 0

        cd = {}
        disease_num_cards = {}
        for d in disease_list:
            disease_num_cards[d] = 0
        for c in current_player.cards.keys():
            # try/except to handle event cards in player's hand
            try:
                cd[c] = (
                    current_player.cards[c].disease,
                    current_player.cards[c].city,
                    current_player.cards[c],
                )
                disease_num_cards[cd[c][0]] += 1
            except:
                continue

        # print cards in player's hand
        print("Player has the following cards:")
        for c in cd.keys():
            print(c, cd[c][0])

        # Typically 5 cards of same disease are required to cure
        # With Scientist, only 4 cards are required
        cards_required = 5
        if players[current_player.name].role == "Scientist":
            cards_required = 4

        # Determine which disease the player has the most of
        # Since at least 4 cards of the same disease are required and the
        # hand limit is 7, at most one disease should be curable per player per turn
        cards_attained = max(disease_num_cards.values())
        cure_disease = [
            d_max
            for d_max in disease_num_cards.keys()
            if disease_num_cards[d_max] == cards_attained
        ][0]

        if cards_attained < cards_required:
            print(
                "Only "
                + str(cards_attained)
                + " "
                + cure_disease
                + " cards attained ("
                + str(cards_required)
                + " required)"
            )
            return 0

        # If more cards are present than needed, allow player to select which cards of the cured disease to hold onto
        elif cards_attained > cards_required:
            print(
                "Only "
                + str(cards_required)
                + " "
                + cure_disease
                + " cards required ("
                + str(cards_attained)
                + " attained)"
            )
            print(
                "Choose which "
                + str(cards_attained - cards_required)
                + " cards to keep"
            )
            for k in range(cards_attained - cards_required):
                c_k = input().strip()
                try:
                    del cd[c_k]
                except:
                    print(
                        "City name not recognized. "
                        + str(cards_required)
                        + " "
                        + cure_disease
                        + " cards will be selected by hand order."
                    )
                    break
        cards_to_cure = []
        cards_to_cure = [c_c[2] for c_c in cd.values() if c_c[0] == cure_disease]
        num = 0
        for c_c in cards_to_cure:
            if num == cards_required:
                break
            crd = current_player.play_card(c_c.value)
            player_discard.add_card(crd)
            num += 1
        cured.append(cure_disease)

        print(cure_disease + " disease has been cured")

        check_eradicated()

        return 1

    # Heal Cubes
    def heal(command):
        global players
        global cities
        global current_player
        global cured
        global eradicated

        # Figure out which disease to treat, if multiple
        try:
            space_ind = command.index(" ")
            disease_name = command[space_ind + 1 :]
        except:
            disease_name = current_player.location.default_disease
            print(
                "No disease recognized.  Checking default disease for "
                + current_player.location.name
                + " ("
                + disease_name
                + ")"
            )
        if not (current_player.location.diseases[disease_name] > 0):
            print(
                "No "
                + disease_name
                + " cubes present in "
                + current_player.location.name
            )
            return 0

        quant = 1
        rle = current_player.role
        # Medics can heal all cubes of given disease with one move
        # Anyone can heal all cubes of cured disease with one move
        if rle == "Medic" or disease_name in cured:
            quant = current_player.location.diseases[disease_name]

        try:
            current_player.location.heal(disease=disease_name, quantity=quant)
            print(
                str(quant)
                + " "
                + disease_name
                + " cubes have been removed from "
                + current_player.location.name
                + " ["
                + str(current_player.location.diseases[disease_name])
                + " "
                + disease_name
                + " cubes remain]"
            )

            check_eradicated()
            #            if disease_name in cured and disease_cubes[disease_name] == 24:
            #                eradicated.append(disease_name)
            #                print(disease_name+" has been eradicated")
            return 1
        except:
            print("Failure to heal.")
            return 0

    # Share Knowledge
    def share(command):
        global cities
        global players
        global current_player
        global player_discard

        try:
            space_ind = command.index(" ")
            city_player = command[space_ind + 1 :]
            #                    print("city_player: "+city_player)
            city_name = ""
            # Searches whether each city in city dictionary is in p_act input
            for c in cities.keys():
                #                        print(": "+c)
                if c in command:
                    city_name = c
                    break
            #                    print("city_name: "+city_name)
            if city_name == "":
                print("City name not recognized.")
                return 0

            player_name = city_player[len(city_name) + 1 :]

        except:
            print("Could not identify parties for 'Share Knowledge'.")
            return 0

        # Make sure giving player has the card
        if city_name not in current_player.cards.keys():
            print(
                "Giving player must have the city card in order to 'Share Knowledge'."
            )
            return 0

        # Ensure both players are in the same city
        if current_player.location != players[player_name].location:
            print(
                "Giving and receiving players must be in the same city in order to 'Share Knowledge'."
            )
            return 0

        # Ensure either card being transferred matches current city or sharing player's role is "Researcher"
        if (
            current_player.location.name != city_name
            and current_player.role != "Researcher"
        ):
            print(
                "City card must match current location OR current player must be a 'Researcher'."
            )
            return 0

        crd = current_player.play_card(city_name)
        players[player_name].cards[city_name] = crd
        print(
            city_name
            + " city card has been transferred from "
            + current_player.name
            + " to "
            + player_name
        )

        card_limit(player_name)

        return 1

    # Take Card (from Researcher only)
    def take(command):
        global cities
        global players
        global current_player
        global player_discard

        try:
            space_ind = command.index(" ")
            city_name = command[space_ind + 1 :]

            # Checks whether city exists (also confirms not an action card)
            assert city_name in cities.keys()

            from_player_name = ""
            for plyr in player_list:
                if plyr == current_player.name:
                    continue
                if city_name in players[plyr].cards.keys():
                    from_player_name = plyr
                    break
            if from_player_name == "":
                print("No player found with " + city_name + " card")
                return 0
        except:
            print("City name not recognized.")
            return 0

        # Ensure both players are in the same city
        if current_player.location != players[from_player_name].location:
            print(
                "In order to 'Take', player must be in the same city as 'Researcher'."
            )
            return 0

        # Ensure player being taken from is a 'Researcher'
        if players[from_player_name].role != "Researcher":
            print("In order to 'Take', player taken from must be 'Researcher'.")
            return 0

        crd = players[from_player_name].play_card(city_name)
        current_player.cards[city_name] = crd
        print(
            city_name
            + " city card has been transferred from "
            + from_player_name
            + " to "
            + current_player.name
        )

        card_limit(current_player.name)

        return 1

    # Retrieve Event Card (Contingency Planner only)
    def retrieve(command):
        print("Retrieve not yet available.")
        return 0

    command = input().strip()
    cmd = command.lower()

    # See if player is requesting information rather than trying to act
    try:
        exec(command)
        return i

    except:

        if "play" in cmd:
            return i + play(command)
        elif "move" in cmd:
            return i + move(command)
        elif "build" in cmd:
            return i + build(command)
        elif "heal" in cmd or "treat" in cmd:
            return i + heal(command)
        elif "cure" in cmd:
            return i + cure(command)
        elif "share" in cmd:
            return i + share(command)
        elif "take" in cmd:
            return i + take(command)
        elif "retrieve" in cmd:
            return i + retrieve(command)
        elif "skip" in cmd:
            return 4
        else:
            print("Command not recognized")
            return i


win = False

# Game ends when outbreaks reach 8, player deck runs out of cards, or any disease cube supply is exhausted
# (or player wins)
j = 0  # Turns
while (
    not win
    and outbreaks < 8
    and len(player_deck.cards) > 0
    and min([a for a in disease_cubes.values()]) >= 0
):

    # Game continues
    current_player = players[player_list[player_ind]]
    active_player = players[player_list[player_ind]]

    #    summary_status()
    detail_status()

    print("Player '" + active_player.name + "' turn")

    infect_cities = True

    # Complete (4) actions
    i = 0
    while i < 4:
        win = check_win()
        if check_win():
            break

        #        if current_player.role == "Dispatcher":
        #            print("Enter player to move")
        #            a_p = input().strip()
        #            try:
        #                active_player = players[a_p]
        #            except:
        #                print("Player name not recognized - defaulting to current player action")
        #                active_player = current_player

        print("Complete (" + str(4 - i) + ") Actions")
        i = action(i)

    #        p_act = input().strip()

    ##            print("Action detected")
    #
    #
    #            if "Play" in p_act or "play" in p_act:
    #
    #
    #            elif "Move" in p_act or "move" in p_act:
    #
    #
    #            #Build a research station
    #            elif "Build" in p_act or "build" in p_act:
    #
    #
    #            #Discover a cure
    #            elif "Cure" in p_act or "cure" in p_act:
    #
    #
    #
    #            #Treat/Heal disease
    #            elif "Treat" in p_act or "treat" in p_act or "Heal" in p_act or "heal" in p_act:
    #
    #
    #            #Share knowledge ("Share" or "Take")
    #            #"Share" (give player card to another player): "Share "+city_name+" "+receiving_player_name
    #            elif "Share" in p_act or "share" in p_act:
    #
    #
    #            #"Take" (take player card from another player - requires that player taken from is "Researcher"): "Take "+city_name
    #            elif "Take" in p_act or "take" in p_act:
    #
    #
    #            elif "Skip" in p_act or "skip" in p_act:
    #                i = 4
    #                continue

    win = check_win()
    if win:
        break

    # MOVE THIS CODE TO "impose_quarantine()"
    # q_dict = {"Red":[list of cities under red quarantine], "Blue":[...]}
    q_dict = {}
    for disease in disease_list:
        q_dict[disease] = []
        if disease in eradicated:
            continue
        for cit in cities.keys():
            cities[cit].quarantine[disease] = False

    for p_name in players.keys():
        if players[p_name].role == "Quarantine Specialist":
            for disease in disease_list:
                q_dict[disease].append(players[p_name].location)
                q_dict[disease] += players[p_name].location.neighbors
        if players[p_name].role == "Medic":
            for disease in cured:
                q_dict[disease].append(players[p_name].location)

    for disease in q_dict.keys():
        for cit in q_dict[disease]:
            cit.quarantine[disease] = True

    print("Last chance to play event card before 'Draw (2) Player Cards' step")
    cmd = input().strip()
    if "play" in cmd.lower():
        try:
            space_ind = cmd.index(" ")
            event_card_value = cmd[space_ind + 1 :]
            owner_name = ""
            for plyr in player_list:
                if event_card_value in players[plyr].cards.keys():
                    owner_name = plyr
                    break
            if owner_name == "":
                print("Card not found in any player's hand.")
            else:
                crd = players[owner_name].play_card(event_card_value)
                try:
                    assert event_card_value not in players[owner_name].cards.keys()
                    player_discard.add_card(crd)
                except:
                    print("Fail :(")
        except:
            print("Event card value not recognized.")

    # Draw (2) player cards
    for draw_ind in range(2):
        next_card = current_player.draw_card(player_deck)
        try:
            print(
                "Player "
                + current_player.name
                + " draws "
                + next_card.value
                + " ("
                + next_card.disease
                + ") card"
            )
        except:
            print(
                "Player " + current_player.name + " draws " + next_card.value + " card"
            )
        if next_card.value == "Epidemic!":
            next_card.play()
            player_discard.add_card(next_card)

    for plyr_name in players.keys():
        card_limit(plyr_name)
    #        while len(players[plyr_name].cards.keys()) > 7:
    #            print("Player "+plyr_name+ " has "+str(len(players[plyr_name].cards.keys()))+
    #                  " cards in hand (7 allowed). Enter city card to discard or event card to play.")
    #            crd = input().strip()
    #
    #            try:
    #                crd_played = players[plyr_name].play_card(crd)
    #                assert crd not in players[owner_name].cards.keys()
    #                player_discard.add_card(crd_played)
    #            except:
    #                print("Card value not recognized.")

    print("Last chance to play event card before 'Infect Cities' step")
    cmd = input().strip()
    if "play" in cmd.lower():
        try:
            space_ind = cmd.index(" ")
            event_card_value = cmd[space_ind + 1 :]
            owner_name = ""
            for plyr in player_list:
                if event_card_value in players[plyr].cards.keys():
                    owner_name = plyr
                    break
            if owner_name == "":
                print("Card not found in any player's hand.")
            else:
                crd = players[owner_name].play_card(event_card_value)
                try:
                    assert event_card_value not in players[owner_name].cards.keys()
                    player_discard.add_card(crd)
                except:
                    print("Fail :(")
        except:
            print("Event card value not recognized.")

    # MOVE THIS CODE TO "impose_quarantine()"
    # q_dict = {"Red":[list of cities under red quarantine], "Blue":[...]}
    q_dict = {}
    for disease in disease_list:
        q_dict[disease] = []
        if disease in eradicated:
            continue
        for cit in cities.keys():
            cities[cit].quarantine[disease] = False

    for p_name in players.keys():
        if players[p_name].role == "Quarantine Specialist":
            for disease in disease_list:
                q_dict[disease].append(players[p_name].location)
                q_dict[disease] += players[p_name].location.neighbors
        if players[p_name].role == "Medic":
            for disease in cured:
                q_dict[disease].append(players[p_name].location)

    for disease in q_dict.keys():
        for cit in q_dict[disease]:
            cit.quarantine[disease] = True

    # Infect (infection_rate) cities
    if infect_cities:
        for c_i in range(infection_rate):
            inf_crd = infect_deck.draw_top()
            outbreaks = inf_crd.play(outbreaks)
            infect_discard.add_card(inf_crd)
            for disease in q_dict.keys():
                for cit in q_dict[disease]:
                    cit.quarantine[disease] = True

    # Increment player index for next turn
    player_ind = (player_ind + 1) % num_players
    j += 1


if outbreaks >= 8:
    print("Game over - too many outbreaks")
if len(player_deck.cards) == 0:
    print("Game over - no player cards left")
if min([a for a in disease_cubes.values()]) < 0:
    print("Game over - out of disease cubes")
