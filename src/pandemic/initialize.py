# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 08:47:45 2021

@author: Alexander Lakocy
"""


disease_list = ["Blue", "Yellow", "Black", "Red"]

infection_rates = [2, 2, 2, 3, 3, 4, 4]

research_stations = 6

epidemics = {"easy": 4, "intermediate": 5, "hard": 6}

roles = {
    "Scientist": ["Need only (4) city cards of the same color to discover cure"],
    "Researcher": [("As an action, may give (or another player may take) " 
                    "any city card from player's hand. "
                    "Both players must be in the same city.")],
    "Medic": ["Remove all cubes of one color when treating disease",
              ("Automatically (no action required) remove cubes of ",
               "cured diseases from the city player occupies "
               "(and prevent from being placed there)")],
    "Quarantine Specialist": [("Prevent infecting city player is in and "
                              "all adjacent cities")],
    "Operations Expert": [("As an action, may construct research stations in "
                           "current city without using the city card"),
                        # ("Once per turn, as an action, may fly from a "
                          # "city with a research station to any city by "
                          # "discarding any city card")  #Ability not yet active
                          ],
    # "Contingency Planner": [("As an action, may retrieve discarded event card."
    #                          "Retrieved card does not apply to hand count. "
    #                          "After playing retrieved card, "
    #                          "remove from the game. ")],
    "Dispatcher": ["May move another player as if your own",
                   ("As an action, may move any player to a city "
                    "with another player")],

    # Expansion Roles???:
    # Field Operative: Once per turn, as an action, may move (1) cube from current city to role card
    #                 May cure a disease using (3) city cards plus (3) matching cubes from role card
    # Archivist: May keep up to (8) cards in hand at a time
    #           Once per turn, as an action, may retrieve discarded city card corresponding to player's current city
    # Generalist: May do up to (5) actions each turn
    # Epidemiologist: Once during player's turn, may take any city card from another player in the same city
    # Troubleshooter: May view as many upcoming infection cards as the current infection rate
    #                Once per turn, as an action, may fly to a city for which the player owns the city card without discarding the card
    }

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

#city_data = [(city1_name, city1_pop, city1_default_disease),...]
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