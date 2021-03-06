# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 20:45:02 2018

@author: alakocy
"""

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
# Dictionary of roles and definitions
global roles

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


from constants import (QTY_CUBES,
                       CUBE_LIMIT,
                       MAX_OUTBREAKS,
                       ACTIONS_PER_TURN,
                       CARDS_TO_CURE, 
                       MAX_CARDS_IN_HAND, 
                       FORECAST_LIMIT,
                       )

from initialize import (disease_list,
                        infection_rates,
                        research_stations,
                        epidemics,
                        roles,
                        pairwise_dict,
                        city_data,
                        )

from objects import (CardDeck,
                    EventCard,
                    CityCard,
                    EpidemicCard,
                    InfectCard,
                    City,
                    Player,
                    )

from board_setup import (assign_roles,
                         generate_cities,
                         generate_neighbors,
                         assign_diseases,
                         )

from player_functions import (list_actions,
                              infection_status,
                              player_status,
                              team_status,
                              card_status,
                              discarded_player_cards,
                              discarded_infection_cards,
                              locate_players,
                              adjacent_cities,
                              summary_status,
                              detail_status,
                              list_commands,
                              )

from operations import (check_win,
                        impose_quarantine,
                        card_limit,
                        check_eradicated,
                        medic_auto_heal,
                        government_grant,
                        one_quiet_night,
                        forecast,
                        airlift,
                        resilient_population,
                        epidemic,
                        combine,
                        )


# Assign Game Variables
#active_player is the player being moved. Generally same as current_player
# unless e.g. Dispatcher (current player) is moving another player (active)
active_player = None
current_player = None
infect_cities = True


disease_cubes = {}
for disease in disease_list:
    disease_cubes[disease] = QTY_CUBES

outbreaks = 0
infection_rate = infection_rates.pop(0)

cured = []
eradicated = []


###############################################################################
# Game Setup

neighbor_pairs = []

for cityA in pairwise_dict.keys():
    for cityB in pairwise_dict[cityA]:
        neighbor_pairs.append((cityA, cityB))

city_info_list = []

for (c, p, d) in city_data:
    city_info_list.append((c, p))

disease_dict = {}

for (c, p, d) in city_data:
    disease_dict[c] = d

cities = generate_cities(city_info_list)

cities = generate_neighbors(neighbor_pairs, cities)

cities = assign_diseases(disease_dict, cities)

# disease_dict = {"New York":"Blue","Montreal":"Blue","Washington":"Blue","Chicago":"Blue",
#                "Atlanta":"Yellow","Miami":"Yellow","Mexico City":"Yellow","Los Angeles":"Yellow",
#                "San Francisco":"Red"}





research_stations = cities["Atlanta"].build(research_stations)









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
    print("Enter Player %i Name:" %i)
    player_list.append(input().strip())

print("Enter Difficulty (Easy, Intermediate, Hard):")
while True:
    try:
        difficulty = input().strip().lower()
        assert difficulty in epidemics.keys()
        break
    except:
        print("Difficulty not recognized")


###############################################################################
# Card Decks:


print("Constructing Card Decks...")

num_epidemics = epidemics[difficulty]

event_card_list = [
    "Government Grant",
    "One Quiet Night",
    "Forecast",
    "Airlift",
    "Resilient Population",
]
poss_roles = list(roles.keys())

players = assign_roles(player_list, poss_roles)

player_cards = []
infect_cards = []

for city_obj in cities.values():
    player_cards.append(city_obj.gen_city_card())
    infect_cards.append(city_obj.gen_inf_card())

for e_card in event_card_list:
    player_cards.append(EventCard(e_card))

player_deck = CardDeck(player_cards)
player_deck.shuffle()

# Draw city cards before placing "Epidemic" cards in deck
num_start_cards = 6 - num_players
for p in players.keys():
    players[p].set_location(cities["Atlanta"])
    cities["Atlanta"].move_to(players[p])
    for i in range(num_start_cards):
        players[p].draw_card(player_deck)

# Divide player deck into equal sub-decks to distribute "Epidemic" cards
sub_decks = player_deck.divide(num_epidemics)

# Add one "Epidemic" card to each sub-deck, then shuffle sub-deck
for sub in sub_decks:
    a = EpidemicCard()
    sub.add_card(a)
    sub.shuffle()

player_deck = combine(sub_decks)

infect_deck = CardDeck(infect_cards)
infect_deck.shuffle()

# Create empty decks for discard piles
player_discard = CardDeck(None)
infect_discard = CardDeck(None)

###############################################################################
# Initial Infections

print("\nRoles have been assigned:")
for p in players:
    role = players[p].role
    print("\n%s: %s" %(players[p].name, role))
    for ability in roles[role]:
        print("%s: %s" %(role, ability))

print("\nCities will now be infected")

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

print("Player %s has the highest population city card (%s, %i)"
    %(max_player.name, max_city.name, max_pop)
)
print("Player '%s' will go first" %max_player.name)

active_player = max_player
player_ind = player_list.index(active_player.name)




###############################################################################
###############################################################################
# Gameplay


###############################################################################
# Actions

# action function is called each time actions remain for a player's turn
# argument i (int) is number of actions remaining
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
            space_ind = command.index(" ")  #Switch to split command
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
                space_ind = command.index(" ")  #Code smells: change to split
                rem_cmd = command[space_ind + 1 :]
                found = False
                for plyr_name in players.keys():
                    if plyr_name in rem_cmd[: len(plyr_name)]:
                        dest_city_name = rem_cmd[
                            rem_cmd.index(plyr_name) + len(plyr_name) + 1 :
                        ] ##Code smells: change to split
                        if dest_city_name not in cities.keys():
                            continue
                        else:
                            found = True
                            active_player = players[plyr_name]
                            print("Current player is 'Dispatcher'. "
                                "Move player '%s' to %s"
                                %(plyr_name, dest_city_name)
                            )
                            break
                if not found:
                    raise Exception
            except:
                print("Current player is 'Dispatcher'. Enter player to move:")
                act_plyr_name = input().strip()
                try:
                    active_player = players[act_plyr_name]  ##Switch to players.get(act_plyr_name, current_player.name)
                    print("Active player is %s" %act_plyr_name)

                except:
                    print(
                        "Player name not recognized. Defaulting to %s"
                        %current_player.name
                    )
                    active_player = players[current_player.name]
                print("Enter destination city:")
                dest_city_name = input().strip()

        else:
            try:
                space_ind = command.index(" ")  ##Switch to split
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
                "Drive/Ferry from %s to %s"
                %(active_player.location.name, dest_city.name)
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
                "Shuttle Flight from %s to %s"
                %(active_player.location.name, dest_city.name)
            )
            active_player.move(dest_city.name)

        # Dispatcher ability: Move any pawn (active) to any city with another pawn
        elif current_player.role == "Dispatcher" and len(dest_city.pawns) > 0:
            print(
                "Dispatcher sends %s from %s to %s"
                %(active_player.name,
                active_player.location.name,
                dest_city.name)
            )
            active_player.move(dest_city.name)

        else:

            try:

                # Direct Flight - player has destination city card
                if dest_city.name in current_player.cards.keys():
                    print(
                        "Direct Flight to %s requires discarding player card. "
                        "Y to confirm"
                        %dest_city.name
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
                        "Charter Flight to %s requires discarding "
                        "%s player card."
                        "\nY to confirm"
                        %(dest_city.name, active_player.location.name)
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

                # Operations Expert 2nd ability - from a research station, may move to any other city by discarding any city card
                elif (
                    current_player.role == "Operations Expert"
                    and current_player.location.rs
                ):
                    print(
                        "Operations Expert may discard any card to fly from "
                        "the %s research station to %s"
                        %(current_player.location.name, dest_city.name)
                    )
                    print("Player cards:")
                    for c_name in current_player.cards.keys():
                        if type(current_player.cards[c_name]) is CityCard:
                            print("%s (%s)" 
                                  %(c_name, cities[c_name].default_disease))
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
        return 1

    # Build Research Station
    def build(command):
        global players
        global cities
        global current_player
        global research_stations
        global player_discard

        if current_player.location.rs:
            print("Already a research station in %s" 
                  %current_player.location.name)
            return 0
        
        #Is building a research station possible with current player?
        bld = False
        #Does building a research station require a card?
        crd_reqd = True

        if current_player.role == "Operations Expert":
            bld = True
            crd_reqd = False
            print(
                "Build research station in %s does not require a card."
                %current_player.location.name
            )
        elif active_player.location.name in current_player.cards.keys():
            bld = True
            print(
                "Build research station in %s requires discarding player card."
                %current_player.location.name
            )
        try:
            assert bld
            print("Enter Y to confirm")
            con = input().strip()
            if con.lower() == "y":
                if research_stations == 0:
                    print(
                        "No available research stations. "
                        "Enter city to remove research station from first."
                    )
                    cty_name = input().strip()
                    try:
                        research_stations = cities[cty_name].remove_rs(
                            research_stations
                        )
                    except:
                        print(
                            "City name not recognized. "
                            "Cancel building research station"
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
        # Scientist special ability moved to player attribute
        cards_required = current_player.cards_to_cure

        # Determine which disease the player has the most of
        # Since at least 4 cards of the same disease are required and the
        # hand limit is 7, at most one disease should be curable per player per turn
        # With Archivist expansion role, possible to have 8 cards in hand and
        # one on table, but still not enough to have 5 of two diseases
        cards_attained = max(disease_num_cards.values())
        cure_disease = [
            d_max
            for d_max in disease_num_cards.keys()
            if disease_num_cards[d_max] == cards_attained
        ][0]

        if cards_attained < cards_required:
            print(
                "Only %i %s cards attained (%i required)"
                %(cards_attained, cure_disease, cards_required)
            )
            return 0

        # If more cards are present than needed, allow player to select which cards of the cured disease to hold onto
        elif cards_attained > cards_required:
            print(
                "Only %i %s cards required (%s attained)"
                %(cards_required, cure_disease, cards_attained)
            )
            print(
                "Choose which %i cards to keep"
                %(cards_attained - cards_required)
            )
            for k in range(cards_attained - cards_required):
                c_k = input().strip()
                try:
                    del cd[c_k]
                except:
                    print(
                        "City name not recognized. "
                        "%i %s cards will be selected by hand order"
                        %(cards_required, cure_disease)
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

        print("%s disease has been cured" %cure_disease)

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
            space_ind = command.index(" ")  ##Switch to split()
            disease_name = command[space_ind + 1 :]  #Feature: add support for removing multiple disease cubes
        except:
            disease_name = current_player.location.default_disease
            print(
                "No disease recognized.  Checking default disease for %s (%s)"
                %(current_player.location.name, str(disease_name))
            )
        if not (current_player.location.diseases[disease_name] > 0):
            print(
                "No %s cubes present in %s"
                %(disease_name, current_player.location.name)
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
            print("%i %s cubes have been removed from %s [%i %s cubes remain]"
                  %(quant, 
                    disease_name, 
                    current_player.location.name, 
                    current_player.location.diseases[disease_name],
                    disease_name)
            )

            check_eradicated()
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
            space_ind = command.index(" ") ##Code smells: Use split
            city_player = command[space_ind + 1 :]
            #                    print("city_player: "+city_player)
            city_name = ""
            # Searches whether each city in city dictionary is in p_act input
            for c in cities.keys():
                if c in command:
                    city_name = c
                    break
            if city_name == "":
                print("City name not recognized.")
                return 0

            player_name = city_player[len(city_name) + 1 :]

        except:
            print("Could not identify parties for 'Share Knowledge'.")  ##Condense failures to share into single failure variable, print on fail0
            return 0

        # Make sure giving player has the card
        if city_name not in current_player.cards.keys():
            print(
                "Giving player must have the city card"
                "in order to 'Share Knowledge'."
            )
            return 0

        # Ensure both players are in the same city
        try:
            assert players[player_name].location != ""
        except:
            print("Receiving player name not recognized")
            return 0
        if current_player.location != players[player_name].location:
            print(
                "Giving and receiving players must be in the same city "
                "in order to 'Share Knowledge'."
            )
            return 0

        # Ensure either card being transferred matches current city or sharing player's role is "Researcher"
        if (
            current_player.location.name != city_name
            and current_player.role != "Researcher"
        ):
            print(
                "City card must match current location OR current player"
                "must be a 'Researcher'."
            )
            return 0

        crd = current_player.play_card(city_name)
        players[player_name].cards[city_name] = crd
        print("%s city card has been transferred from %s to %s"
            %(city_name, current_player.name, player_name)
        )

        card_limit(player_name)

        return 1  #Executes if share() call is successful (counts as 1 move)

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
                print("No player found with %s card" %city_name)  ##Consolidate fail messages
                return 0
        except:
            print("City name not recognized.")
            return 0

        # Ensure both players are in the same city
        if current_player.location != players[from_player_name].location:
            print(
                "In order to 'Take', player must be in the "
                "same city as 'Researcher'."
            )
            return 0

        # Ensure player being taken from is a 'Researcher'
        if players[from_player_name].role != "Researcher":
            print("In order to 'Take', player taken from must "
                  "be 'Researcher'.")
            return 0

        crd = players[from_player_name].play_card(city_name)
        current_player.cards[city_name] = crd
        print("%s city card has been transferred from %s to %s"  #Code smells: possible duplicate
            %(city_name, from_player_name, current_player.name)
        )

        card_limit(current_player.name)

        return 1

    # Retrieve Event Card (Contingency Planner only)
    def retrieve(command):
        print("Retrieve not yet available.")
        return i

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
            return current_player.actions_per_turn
        else:
            print("Command not recognized")
            return i


win = False

list_actions()

# Game ends when outbreaks reach MAX_OUTBREAKS, 
#player deck runs out of cards, or any disease cube supply is exhausted
# (or player wins)
j = 0  # Turns
while (
    not win
    and outbreaks < MAX_OUTBREAKS
    and len(player_deck.cards) > 0
    and min([a for a in disease_cubes.values()]) >= 0
):

    # Game continues
    current_player = players[player_list[player_ind]]
    active_player = players[player_list[player_ind]]

    #    summary_status()
    detail_status()

    print("Player %s's turn" %active_player.name)
    
    #Flag - infect_cities will generally happen unless stopped by event card.
    #       reset at the start of each player's turn
    infect_cities = True

    # Complete (ACTIONS_PER_TURN) actions
    i = 0
    while i < current_player.actions_per_turn:  ###ACTIONS_PER_TURN
        #Check whether win condition achieved before action
        win = check_win()  #Code smells - win variable not used, is necessary?
        if check_win():
            break

        print("Complete (%i) Actions" %(current_player.actions_per_turn - i))
        i = action(i) #Pass i (actions remaining this turn). action() returns
                        # 0 or 1 depending on whether a valid command was passed

    win = check_win()  #Code smells - win variable not used, is necessary?
    if win:
        break

    #q_dict {disease1:[quarantined_city_1, q_city_2,...], disease2:[...]}
    #Empty q_dict
    q_dict = {}
    for disease in disease_list:
        q_dict[disease] = []
        #If the disease is eradicated, city.infect() will not infect cities
        if disease in eradicated:
            continue
        #Loop through all cities, not just cities where default_disease==disease
        # in case an outbreak at a border city has caused non-default infection
        for cit in cities.keys():
            cities[cit].quarantine[disease] = False

    for p_name in players.keys():
        #Add all cities at and around Q.S. to quarantine dictionary
        if players[p_name].role == "Quarantine Specialist":
            for disease in disease_list:
                q_dict[disease].append(players[p_name].location)
                q_dict[disease] += players[p_name].location.neighbors
        #For any cured disease, prevent placement of new disease cubes in
        # the city where the Medic is located (part of auto-heal ability)
        if players[p_name].role == "Medic":
            for disease in cured:
                q_dict[disease].append(players[p_name].location)

    for disease in q_dict.keys():
        #Assign quarantine attribute for applicable diseases to all cities in q_dict
        for cit in q_dict[disease]:
            cit.quarantine[disease] = True

    print("Last chance to play event card before 'Draw (2) Player Cards' step")
    cmd = input().strip()
    if "play" in cmd.lower():
        try:
            space_ind = cmd.index(" ")  #Code smells: replace with split
            # figure out which card is to be played
            event_card_value = cmd[space_ind + 1 :]
            owner_name = ""
            # determine whether card is in any player's hand
            for plyr in player_list:
                if event_card_value in players[plyr].cards.keys():
                    owner_name = plyr
                    break
            if owner_name == "":
                print("Card not found in any player's hand.")
            else:
                crd = players[owner_name].play_card(event_card_value)
                try:
                    #Confirm card was played
                    assert event_card_value not in players[owner_name].cards.keys()
                    player_discard.add_card(crd)  #Code smells: possibly add the discard functionality to player.play_card()
                except:
                    print("Fail :(")
        except:
            print("Event card value not recognized.")

    # Draw (2) player cards
    for draw_ind in range(2):
        next_card = current_player.draw_card(player_deck)
        try:
            print(
                "Player %s draws %s (%s) card" 
                %(current_player.name,
                  next_card.value,
                  next_card.disease)
                )
        except:
            print(
                "Player %s draws %s card"
                %(current_player.name, next_card.value)
                )
        if next_card.value == "Epidemic!":
            next_card.play()
            player_discard.add_card(next_card)

    for plyr_name in players.keys():
        card_limit(plyr_name)

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

    # MOVE THIS CODE TO operations.impose_quarantine()
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


if outbreaks >= MAX_OUTBREAKS:  
    print("Game over - too many outbreaks")
if len(player_deck.cards) == 0:
    print("Game over - no player cards left")
if min([a for a in disease_cubes.values()]) < 0:
    print("Game over - out of disease cubes")
