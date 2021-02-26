# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 19:11:52 2018

@author: alakocy
"""

import wikipedia

def dist_between(cityA,cityB):
    #Still needed
    return 1

def find_pop(city):
    try: 
        pt = wikipedia.page(city,"lxml")
        print("As-is")
    except: 
        pt = wikipedia.page(city+" City","lxml")
        print("+ 'City'")
    print(pt.summary)
    a = pt.content.find("population")
    b = pt.content[a:a+30].find(",")
    if b==-1:
        a = pt.content.find("residents")
        b = pt.content[a-40:a].find(",")
    if b==-1:
        a0 = pt.content.find("Demographics")
        a = pt.content[a0:].find("population")
        b = pt.content[a:a+30].find(",")
    print(b)
    p = ""
    since_comma = 0
    found_first = False
    for d in pt.content[a+b-10:a+30]:
        if d==',': 
            since_comma = 0
            found_first = True
        if since_comma > 3 and found_first: break
        since_comma += 1
        try: int(d)
        except: continue
        p += d
    if p=="": 
        print(pt.content[a-40:a+30])
        return 0
    return int(p)#,a,b,pt

#p, a, b, pt = find_pop("New York")
#print(p)
##print(pt.content[a:a+30])
##print(pt.content[a+b-10:a+30])    
#
#
#pp, ap, bp, ptp = find_pop("Paris")
#print(pp)
#print(ptp.content[ap:ap+30])
#
#pr, ar, br, ptr = find_pop("Rome")
#print(ptr.content[ar-40:ar])

city_pool = ["New York","Atlanta","Chicago","Montreal","Washington","San Francisco",
 "Los Angeles","Miami","Mexico City","Bogota","Lima","Santiago","Buenos Aires","Sao Paulo","Lagos","Kinshasha","Johannesburg","Khartoum", "St. Petersburg","Madrid","London","Essen","Paris","Milan",
"Cairo","Algiers","Istanbul","Moscow","Tehran","Baghdad","Riyadh","Karachi","Delhi","Mumbai","Chennai","Kolkata",
"Bangkok","Jakarta","Sydney","Manila","Ho Chi Minh City","Hong Kong","Taipei","Osaka","Tokyo","Seoul","Beijing","Shanghai"]

city_pops = []

for city in city_pool:
    print(city)
    city_pops.append((city,find_pop(city)))
