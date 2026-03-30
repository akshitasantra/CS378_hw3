import unified_planning
from unified_planning.shortcuts import *
from unified_planning.model import StartTiming, EndTiming

# Disable credits printing as suggested by the engine warning
unified_planning.shortcuts.get_environment().credits_stream = None

# --------------------
# TYPE DEFINITIONS
# --------------------

# Define a type for rooms
room = UserType('room')

# Define types for mobile robots. 
# FIX: Removed the 'mobile_robot' parent type to prevent Tamer's RedefinitionError.
mobile_manipulator = UserType('mobile_manipulator')
mobile_vacuum = UserType('mobile_vacuum')


# --------------------
# FLUENT DEFINITIONS
# --------------------

# tidy(rm): room rm is tidy
tidy = Fluent('tidy', rm=room)

# clean(rm): room rm is clean
clean = Fluent('clean', rm=room)

# connected_rooms(rm1, rm2): rm1 and rm2 are connected (movement allowed)
connected = Fluent('connected_rooms', rm1=room, rm2=room)

# current_room_manipulator(r, rm): robot manipulator r is currently located in room rm
current_room_manipulator = Fluent('current_room_manipulator', r=mobile_manipulator, rm=room)

# current_room_vacuum(r, rm): robot vacuum r is currently located in room rm
current_room_vacuum = Fluent('current_room_vacuum', r=mobile_vacuum, rm=room)

# --------------------
# ACTION: ROBOT MANIPULATOR MOVE BETWEEN ROOMS
# --------------------
# move_room(r, rm_from, rm_to):
move_room_manip = DurativeAction('move_room_manip', r=mobile_manipulator, rm_from=room, rm_to=room)
move_room_manip.set_fixed_duration(30)
rm = move_room_manip.parameter('r')
frm = move_room_manip.parameter('rm_from')
to = move_room_manip.parameter('rm_to')

# Preconditions:
# - robot must be in rm_from
# - rm_from and rm_to must be connected
move_room_manip.add_condition(StartTiming(), current_room_manipulator(rm, frm))
move_room_manip.add_condition(StartTiming(), connected(frm, to))

# Effects:
# - robot leaves rm_from
# - robot arrives in rm_to
move_room_manip.add_effect(StartTiming(), current_room_manipulator(rm, frm), False)
move_room_manip.add_effect(EndTiming(), current_room_manipulator(rm, to), True)

# --------------------
# ACTION: ROBOT VACUUM MOVE BETWEEN ROOMS
# --------------------
# move_room(r, rm_from, rm_to):
move_room_vac = DurativeAction('move_room_vac', r=mobile_vacuum, rm_from=room, rm_to=room)
move_room_vac.set_fixed_duration(30)
rmv = move_room_vac.parameter('r')
frmv = move_room_vac.parameter('rm_from')
tov = move_room_vac.parameter('rm_to')

# Preconditions:
# - robot must be in rm_from
# - rm_from and rm_to must be connected
move_room_vac.add_condition(StartTiming(), current_room_vacuum(rmv, frmv))
move_room_vac.add_condition(StartTiming(), connected(frmv, tov))

# Effects:
# - robot leaves rm_from
# - robot arrives in rm_to
move_room_vac.add_effect(StartTiming(), current_room_vacuum(rmv, frmv), False)
move_room_vac.add_effect(EndTiming(), current_room_vacuum(rmv, tov), True)

# --------------------
# ACTION: TIDY ROOM
# --------------------
# tidy_room(r, rm):
# Only a mobile manipulator can tidy a room it is currently in
tidy_room = DurativeAction('tidy_room', r=mobile_manipulator, rm=room)
tidy_room.set_fixed_duration(300)
tidy_room_robot = tidy_room.parameter('r')
tidy_room_room = tidy_room.parameter('rm')

# Preconditions:
# - manipulator must be in the room
tidy_room.add_condition(StartTiming(), current_room_manipulator(tidy_room_robot, tidy_room_room))

# Effects:
# - room becomes tidy
# - room is no longer clean (tidying may introduce dirt)
tidy_room.add_effect(EndTiming(), tidy(tidy_room_room), True)
tidy_room.add_effect(EndTiming(), clean(tidy_room_room), False)

# --------------------
# ACTION: CLEAN A ROOM
# --------------------
# clean_room(r, rm):
# Only a mobile vacuum can clean a room
# A room must be tidy before it can be cleaned
clean_room = DurativeAction('clean_room', r=mobile_vacuum, rm=room)
clean_room.set_fixed_duration(400)
clean_room_robot = clean_room.parameter('r')
clean_room_room = clean_room.parameter('rm')

# Preconditions:
# - vacuum must be in the room
# - room must already be tidy
clean_room.add_condition(StartTiming(), current_room_vacuum(clean_room_robot, clean_room_room))
clean_room.add_condition(StartTiming(), tidy(clean_room_room))

# Effects:
# - room becomes clean
clean_room.add_effect(EndTiming(), clean(clean_room_room), True)

# --------------------
# Base Problem
# --------------------
# Define a base planning problem containing all shared fluents and actions
problem = Problem('problem')

problem.add_fluent(tidy)
problem.add_fluent(clean)
problem.add_fluent(connected)
problem.add_fluent(current_room_manipulator)
problem.add_fluent(current_room_vacuum)

problem.add_action(move_room_manip)
problem.add_action(move_room_vac)
problem.add_action(tidy_room)
problem.add_action(clean_room)

# =====================
# Map 1
# =====================
def prob1():
    # FIX: Move logic inside the function and give the clone a unique name
    map1 = problem.clone()
    map1.name = 'map1'
    r1 = map1.add_object('r1', room)
    r2 = map1.add_object('r2', room)
    mm1 = map1.add_object('mm1_map1', mobile_manipulator)
    mv1 = map1.add_object('mv1_map1', mobile_vacuum)

    rooms = [r1, r2]
    
    # FIX: Exhaustively initialize all fluents to False to prevent Tamer uninitialized errors
    for r in rooms:
        map1.set_initial_value(clean(r), False)
        map1.set_initial_value(tidy(r), False)
        map1.set_initial_value(current_room_manipulator(mm1, r), False)
        map1.set_initial_value(current_room_vacuum(mv1, r), False)
        for r_other in rooms:
            map1.set_initial_value(connected(r, r_other), False)

    # Connectivity (bidirectional)
    map1.set_initial_value(connected(r1, r2), True)
    map1.set_initial_value(connected(r2, r1), True)

    # Initial robot locations
    map1.set_initial_value(current_room_manipulator(mm1, r1), True)
    map1.set_initial_value(current_room_vacuum(mv1, r1), True)

    # Goal: all rooms tidy and clean
    for r in rooms:
        map1.add_goal(clean(r))
        map1.add_goal(tidy(r))

    return map1

# =====================
# Map 2
# =====================
def prob2():
    map2 = problem.clone()
    map2.name = 'map2'

    nw = map2.add_object('nw', room)
    ne = map2.add_object('ne', room)
    sw = map2.add_object('sw', room)
    se = map2.add_object('se', room)
    mm2 = map2.add_object('mm1_map2', mobile_manipulator)
    mv2 = map2.add_object('mv1_map2', mobile_vacuum)
    
    rooms = [nw, ne, sw, se]

    # Exhaustively initialize all fluents to False
    for r in rooms:
        map2.set_initial_value(clean(r), False)
        map2.set_initial_value(tidy(r), False)
        map2.set_initial_value(current_room_manipulator(mm2, r), False)
        map2.set_initial_value(current_room_vacuum(mv2, r), False)
        for r_other in rooms:
            map2.set_initial_value(connected(r, r_other), False)

    # Define grid connectivity
    map2.set_initial_value(connected(nw, ne), True)
    map2.set_initial_value(connected(ne, nw), True)
    map2.set_initial_value(connected(nw, sw), True)
    map2.set_initial_value(connected(sw, nw), True)
    map2.set_initial_value(connected(se, ne), True)
    map2.set_initial_value(connected(ne, se), True)
    map2.set_initial_value(connected(se, sw), True)
    map2.set_initial_value(connected(sw, se), True)

    # Initial robot locations
    map2.set_initial_value(current_room_manipulator(mm2, sw), True)
    map2.set_initial_value(current_room_vacuum(mv2, ne), True)

    # Goals
    for r in rooms:
        map2.add_goal(clean(r))
        map2.add_goal(tidy(r))

    return map2

# =====================
# Map 3
# =====================
def prob3():
    map3 = problem.clone()
    map3.name = 'map3'

    rm1 = map3.add_object('rm1', room)
    rm2 = map3.add_object('rm2', room)
    rm3 = map3.add_object('rm3', room)
    rm4 = map3.add_object('rm4', room)
    rm5 = map3.add_object('rm5', room)
    rm6 = map3.add_object('rm6', room)
    rm7 = map3.add_object('rm7', room)
    rm8 = map3.add_object('rm8', room)
    corridor = map3.add_object('corridor', room)

    mm3 = map3.add_object('mm1_map3', mobile_manipulator)
    mv3 = map3.add_object('mv1_map3', mobile_vacuum)

    map3.set_initial_value(current_room_manipulator(mm3, corridor), True)
    map3.set_initial_value(current_room_vacuum(mv3, corridor), True)

    map3.set_initial_value(current_room_manipulator(mm3, rm1), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm2), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm3), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm4), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm5), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm6), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm7), False)
    map3.set_initial_value(current_room_manipulator(mm3, rm8), False)

    map3.set_initial_value(current_room_vacuum(mv3, rm1), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm2), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm3), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm4), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm5), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm6), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm7), False)
    map3.set_initial_value(current_room_vacuum(mv3, rm8), False)

    # Room connectivity
    map3.set_initial_value(connected(corridor, rm1), True)
    map3.set_initial_value(connected(rm1, corridor), True)
    map3.set_initial_value(connected(corridor, rm2), True)
    map3.set_initial_value(connected(rm2, corridor), True)
    map3.set_initial_value(connected(corridor, rm3), True)
    map3.set_initial_value(connected(rm3, corridor), True)
    map3.set_initial_value(connected(corridor, rm4), True)
    map3.set_initial_value(connected(rm4, corridor), True)
    map3.set_initial_value(connected(corridor, rm5), True)
    map3.set_initial_value(connected(rm5, corridor), True)
    map3.set_initial_value(connected(corridor, rm6), True)
    map3.set_initial_value(connected(rm6, corridor), True)
    map3.set_initial_value(connected(corridor, rm7), True)
    map3.set_initial_value(connected(rm7, corridor), True)
    map3.set_initial_value(connected(corridor, rm8), True)
    map3.set_initial_value(connected(rm8, corridor), True)

    # Initial room states
    map3.set_initial_value(clean(rm1), False)
    map3.set_initial_value(clean(rm2), False)
    map3.set_initial_value(clean(rm3), False)
    map3.set_initial_value(clean(rm4), False)
    map3.set_initial_value(tidy(rm1), True)
    map3.set_initial_value(tidy(rm2), True)
    map3.set_initial_value(tidy(rm3), True)
    map3.set_initial_value(tidy(rm4), True)

    map3.set_initial_value(clean(rm5), True)
    map3.set_initial_value(clean(rm6), True)
    map3.set_initial_value(clean(rm7), True)
    map3.set_initial_value(clean(rm8), True)
    map3.set_initial_value(tidy(rm5), False)
    map3.set_initial_value(tidy(rm6), False)
    map3.set_initial_value(tidy(rm7), False)
    map3.set_initial_value(tidy(rm8), False)

    map3.set_initial_value(clean(corridor), True)
    map3.set_initial_value(tidy(corridor), True)

    # Goal: all rooms tidy and clean
    map3.add_goal(clean(rm1))
    map3.add_goal(clean(rm2))
    map3.add_goal(clean(rm3))
    map3.add_goal(clean(rm4))
    map3.add_goal(clean(rm5))
    map3.add_goal(clean(rm6))
    map3.add_goal(clean(rm7))
    map3.add_goal(clean(rm8))
    map3.add_goal(tidy(rm1))
    map3.add_goal(tidy(rm2))
    map3.add_goal(tidy(rm3))
    map3.add_goal(tidy(rm4))
    map3.add_goal(tidy(rm5))
    map3.add_goal(tidy(rm6))
    map3.add_goal(tidy(rm7))
    map3.add_goal(tidy(rm8))

    return map3

# ====================
# SOLVER
# ====================
from unified_planning.engines import PlanGenerationResultStatus

def solve(prob):
    # FIX: Using the `with` block ensures memory/engine processes are released between solves
    with OneshotPlanner(name='tamer') as planner:
        result = planner.solve(prob)
        if result.status in [PlanGenerationResultStatus.SOLVED_SATISFICING,
                             PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
            print("SOLVED")
            # FIX: changed `plan` to `result.plan`
            for start, action, duration in result.plan.timed_actions:
                print(f"{float(start)}: {action} [{float(duration)}]")
        else:
            print("NOT SOLVED")
        
print("Map1")
solve(prob1())

print("\nMap2")
solve(prob2())

print("\nMap3")
solve(prob3())