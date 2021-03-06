# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 08:42:06 2021

@author: Alexander Lakocy
"""


###############################################################################
# Internal Functions

# global cured
# global eradicated
# global disease_list
# global disease_cubes

# global players
# global cities

# global player_discard
global infection_rates
global QTY_CUBES
global FORECAST_LIMIT

from objects import CardDeck

from player_functions import infection_status

# Check win condition
def check_win():
    global cured
    global disease_list

    if len(cured) == len(disease_list):
        print(
            "All diseases have been cured. "
            "Pandemic has been contained."
            "\nEnter 'Continue' to keep playing:"
        )
        cmd = input().strip()
        if not "continue" in cmd.lower():
            return False
        return True


# Check whether any cured diseases have been eradicated
def check_eradicated():
    global cured
    global eradicated
    global disease_cubes

    for dis in cured:
        if dis in eradicated:
            continue
        if disease_cubes[dis] == QTY_CUBES:
            eradicated.append(dis)
            print("%s has been eradicated" % dis)


def card_limit(player_name):
    global players
    global cities
    global player_discard
    
    max_cards = players[player_name].max_cards
    
    while len(players[player_name].cards.keys()) > max_cards:
        print(
            "Player %s has %i cards in hand (%i allowed)"
            % (player_name, 
               len(players[player_name].cards.keys()),
               max_cards)
        )

        for c in players[player_name].cards.keys():
            try:
                print("%s (%s)" %(c, players[player_name].cards[c].disease))
            except:
                print("%s (%s)" 
                      %(c, players[player_name].cards[c].instruction)
                      )
        print("Enter city card to discard or event card to play.")
        crd = input().strip()

        try:
            crd_played = players[player_name].play_card(crd)
            player_discard.add_card(crd_played)

        except:
            print("Card value not recognized.")
            continue
    return


def impose_quarantine():
    return

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
                    print("Medic has healed %i %s cubes from %s automatically."
                          %(cities[cur_city_name].diseases[d],
                            d,
                            cur_city_name)
                    )
                    cities[cur_city_name].heal(
                        disease=d, quantity=cities[cur_city_name].diseases[d]
                    )
                    check_eradicated()
    return

# Combines multiple sub-decks (by stacking, no shuffling) and returns the combination
def combine(deck_list):
    card_list = []
    for sub in deck_list:
        card_list += sub.cards
    return CardDeck(card_list)

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
    infect_discard = CardDeck(None)

    num_epidemics -= 1


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
        city_name    #Dead code?

        if research_stations == 0:
            print(
                "No available research stations. "
                "Enter city to remove research station from first."
            )
            com = input().strip()
            try:
                research_stations = cities[com].remove_rs(research_stations)
            except:
                print("City name not recognized. "
                      "Cancel building research station")
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
    top_list = []
    infection_status()
    print("\n")
    print("Top %i cards are:" %FORECAST_LIMIT)
    for c_ind in range(FORECAST_LIMIT):
        crd = infect_deck.draw_top()
        print("%s (%s)" %(crd.value, crd.city.default_disease))
        top_list.append(crd)

    new_list = []
    c_new_ind = 1
    while c_new_ind in range(1, FORECAST_LIMIT+1):
        print("Enter card for position %i (1 will be drawn next)" %c_new_ind)
        c_val = input().strip()
        if c_val == "Stop" or c_val == "stop":
            infect_deck = combine([CardDeck(top_list), infect_deck])
            return False
        for crd in top_list:
            if crd.value == c_val:
                new_list.append(crd)
                break
        if len(new_list) == c_new_ind:
            c_new_ind += 1
        else:
            print("Card value not recognized.")
    infect_deck = combine([CardDeck(new_list), infect_deck])
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
        print("Unable to airlift %s to %s" %(player_name, dest_city_name))
        return False

    # Medic 2nd ability
    medic_auto_heal()

    return True


def resilient_population():
    print("Resilient Population")
    print("Current infection discard pile:")
    global infect_discard
    for crd in infect_discard.cards:
        print("%s (%s)" %(crd.value, crd.city.default_disease))  #Code smells: possible duplicate print statement - use fuction?

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