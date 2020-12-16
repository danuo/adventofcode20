# %%

import re

with open('input') as file:
    lines = file.read()

source_ranges, source_your_ticket, source_nearby_tickets = lines.split('\n\n')

# ─── PARSE INPUT ────────────────────────────────────────────────────────────────

# ─── RANGES 
# ranges = []
ranges_dict = dict()
for string in source_ranges.splitlines():
    name, numbers = string.split(':')
    name = name.replace(' ','')
    match = re.findall('\d+', numbers)
    ranges_dict.update({name: list(map(int, match))})

# ─── MY TICKET 
my_ticket = list(map(int, re.findall('\d+', source_your_ticket)))

# ─── NEARBY TICKETS 
nearby_tickets = []
nearby_tickets_valid = []
for nearby_ticket in source_nearby_tickets.splitlines():
    match = re.findall('\d+', nearby_ticket)
    if match:
        nearby_tickets.append(list(map(int, match)))
        
#%%
# ─── CHALLENGE 1 ────────────────────────────────────────────────────────────────

def number_in_any_range(number):
    # check if number is within one or more ranges
    number_valid = False
    for value in ranges_dict.values():
        if value[0] <= number <= value[1] or value[2] <= number <= value[3]:
            number_valid = True
    return number_valid

error_rate = 0
for ticket in nearby_tickets:
    ticket_valid = True
    for number in ticket:
        if not number_in_any_range(number):
            # number on ticket is outside of every single range
            error_rate += number
            ticket_valid = False
    if ticket_valid:
        nearby_tickets_valid.append(ticket)

# correct for 1 is 20058
print('result 1: ', error_rate)


#%%
# ─── CHALLENGE 2 ────────────────────────────────────────────────────────────────

from math import prod

def add_number_to_solve_dict(number, field):
    # check if number is within one or more ranges
    for key, value in ranges_dict.items():
        if value[0] <= number <= value[1] or value[2] <= number <= value[3]:
            solve_dict[field].update({key: solve_dict[field].get(key, 0) + 1})



solve_dict = {i: dict() for i in range(20)}


#%%


for field in range(20):
    # check number from field from every ticket, put in every range and if valid, put in dict
    for ticket in nearby_tickets_valid:
        number = ticket[field]
        add_number_to_solve_dict(number, field)

# solution_dict: field -> key mapping 
solution_dict = dict()

def filter_counter(item):
    # this function checks, if a field_number->key relation is valid for every single ticket
    # in nearby_tickets_valid
    key, value = item
    condition1 = value == len(nearby_tickets_valid)
    condition2 = key not in solution_dict.values()
    return all([condition1, condition2])

# ─── REMOVE RELATIONS WITH LESS THAN 190 HITS ───────────────────────────────────
for key, ct in solve_dict.items():
    solve_dict[key] = dict(filter(filter_counter, ct.items()))


for _ in range(20):
    # if one field has only one possible key, assign field to key
    # e.i. field 13 -> 'type'

    for key, ct in solve_dict.items():
        if len(ct) == 1:
            solution_dict.update({key: list(ct.keys())[0]})
            
    # remove solved key from solve_dict
    solve_dict_new = dict()
    for key, ct in solve_dict.items():
        new_counter = dict(filter(filter_counter, ct.items()))
        if len(new_counter) > 0:
            solve_dict_new[key] = new_counter
    solve_dict = solve_dict_new


# multiply all ticket values with field name starting with departure
print('result 2: ', prod([my_ticket[key] for key, value in solution_dict.items() if value.startswith('departure')]))

# %%
