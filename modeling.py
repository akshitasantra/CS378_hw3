import unified_planning
from unified_planning.shortcuts import *
from unified_planning.model import StartTiming, EndTiming, ClosedTimeInterval

# Disable credits printing as suggested by the engine warning
unified_planning.shortcuts.get_environment().credits_stream = None

# --------------------
# TYPE DEFINITIONS
# --------------------

room = UserType('room')
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

# moving_manipulator(r): manipulator r is currently in transit
moving_manipulator = Fluent('moving_manipulator', r=mobile_manipulator)

# moving_vacuum(r): vacuum r is currently in transit
moving_vacuum = Fluent('moving_vacuum', r=mobile_vacuum)


# --------------------
# ACTION: ROBOT MANIPULATOR MOVE BETWEEN ROOMS
# --------------------
move_room_manip = DurativeAction('move_room_manip', r=mobile_manipulator, rm_from=room, rm_to=room)
move_room_manip.set_fixed_duration(30)
rm = move_room_manip.parameter('r')
frm = move_room_manip.parameter('rm_from')
to = move_room_manip.parameter('rm_to')

# Preconditions:
# - robot must be in rm_from at start
# - rm_from and rm_to must be connected
# - robot must not already be moving
move_room_manip.add_condition(StartTiming(), current_room_manipulator(rm, frm))
move_room_manip.add_condition(StartTiming(), connected(frm, to))
move_room_manip.add_condition(StartTiming(), Not(moving_manipulator(rm)))

# Effects:
# - robot leaves rm_from at start
# - robot is marked as moving at start
# - robot arrives in rm_to at end
# - robot is no longer moving at end
move_room_manip.add_effect(StartTiming(), current_room_manipulator(rm, frm), False)
move_room_manip.add_effect(StartTiming(), moving_manipulator(rm), True)
move_room_manip.add_effect(EndTiming(), current_room_manipulator(rm, to), True)
move_room_manip.add_effect(EndTiming(), moving_manipulator(rm), False)


# --------------------
# ACTION: ROBOT VACUUM MOVE BETWEEN ROOMS
# --------------------
move_room_vac = DurativeAction('move_room_vac', r=mobile_vacuum, rm_from=room, rm_to=room)
move_room_vac.set_fixed_duration(30)
rmv = move_room_vac.parameter('r')
frmv = move_room_vac.parameter('rm_from')
tov = move_room_vac.parameter('rm_to')

# Preconditions:
# - robot must be in rm_from at start
# - rm_from and rm_to must be connected
# - robot must not already be moving
move_room_vac.add_condition(StartTiming(), current_room_vacuum(rmv, frmv))
move_room_vac.add_condition(StartTiming(), connected(frmv, tov))
move_room_vac.add_condition(StartTiming(), Not(moving_vacuum(rmv)))

# Effects:
# - robot leaves rm_from at start
# - robot is marked as moving at start
# - robot arrives in rm_to at end
# - robot is no longer moving at end
move_room_vac.add_effect(StartTiming(), current_room_vacuum(rmv, frmv), False)
move_room_vac.add_effect(StartTiming(), moving_vacuum(rmv), True)
move_room_vac.add_effect(EndTiming(), current_room_vacuum(rmv, tov), True)
move_room_vac.add_effect(EndTiming(), moving_vacuum(rmv), False)


# --------------------
# ACTION: TIDY ROOM
# --------------------
tidy_room = DurativeAction('tidy_room', r=mobile_manipulator, rm=room)
tidy_room.set_fixed_duration(300)
tidy_room_robot = tidy_room.parameter('r')
tidy_room_room = tidy_room.parameter('rm')

# Preconditions:
# - manipulator must be in the room at start and must stay for the full duration
# - manipulator must not be mid-move
tidy_room.add_condition(StartTiming(), current_room_manipulator(tidy_room_robot, tidy_room_room))
tidy_room.add_condition(ClosedTimeInterval(StartTiming(), EndTiming()), current_room_manipulator(tidy_room_robot, tidy_room_room))
tidy_room.add_condition(ClosedTimeInterval(StartTiming(), EndTiming()), Not(moving_manipulator(tidy_room_robot)))

# Effects:
# - room becomes tidy
# - room is no longer clean (tidying may introduce dirt)
tidy_room.add_effect(EndTiming(), tidy(tidy_room_room), True)
tidy_room.add_effect(EndTiming(), clean(tidy_room_room), False)


# --------------------
# ACTION: CLEAN A ROOM
# --------------------
clean_room = DurativeAction('clean_room', r=mobile_vacuum, rm=room)
clean_room.set_fixed_duration(400)
clean_room_robot = clean_room.parameter('r')
clean_room_room = clean_room.parameter('rm')

# Preconditions:
# - vacuum must be in the room at start and must stay for the full duration
# - room must already be tidy
# - vacuum must not be mid-move
clean_room.add_condition(StartTiming(), current_room_vacuum(clean_room_robot, clean_room_room))
clean_room.add_condition(ClosedTimeInterval(StartTiming(), EndTiming()), current_room_vacuum(clean_room_robot, clean_room_room))
clean_room.add_condition(StartTiming(), tidy(clean_room_room))
clean_room.add_condition(ClosedTimeInterval(StartTiming(), EndTiming()), Not(moving_vacuum(clean_room_robot)))

# Effects:
# - room becomes clean
clean_room.add_effect(EndTiming(), clean(clean_room_room), True)


# --------------------
# Base Problem
# --------------------
problem = Problem('problem')

problem.add_fluent(tidy)
problem.add_fluent(clean)
problem.add_fluent(connected)
problem.add_fluent(current_room_manipulator)
problem.add_fluent(current_room_vacuum)
problem.add_fluent(moving_manipulator)
problem.add_fluent(moving_vacuum)

problem.add_action(move_room_manip)
problem.add_action(move_room_vac)
problem.add_action(tidy_room)
problem.add_action(clean_room)


# =====================
# Map 1
# =====================
def prob1():
    map1 = problem.clone()
    map1.name = 'map1'
    r1 = map1.add_object('r1', room)
    r2 = map1.add_object('r2', room)
    mm1 = map1.add_object('mm1_map1', mobile_manipulator)
    mv1 = map1.add_object('mv1_map1', mobile_vacuum)

    rooms = [r1, r2]

    for r in rooms:
        map1.set_initial_value(clean(r), False)
        map1.set_initial_value(tidy(r), False)
        map1.set_initial_value(current_room_manipulator(mm1, r), False)
        map1.set_initial_value(current_room_vacuum(mv1, r), False)
        for r_other in rooms:
            map1.set_initial_value(connected(r, r_other), False)

    # Moving fluents start False
    map1.set_initial_value(moving_manipulator(mm1), False)
    map1.set_initial_value(moving_vacuum(mv1), False)

    # Connectivity (bidirectional)
    map1.set_initial_value(connected(r1, r2), True)
    map1.set_initial_value(connected(r2, r1), True)

    # Initial robot locations
    map1.set_initial_value(current_room_manipulator(mm1, r1), True)
    map1.set_initial_value(current_room_vacuum(mv1, r1), True)

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

    for r in rooms:
        map2.set_initial_value(clean(r), False)
        map2.set_initial_value(tidy(r), False)
        map2.set_initial_value(current_room_manipulator(mm2, r), False)
        map2.set_initial_value(current_room_vacuum(mv2, r), False)
        for r_other in rooms:
            map2.set_initial_value(connected(r, r_other), False)

    # Moving fluents start False
    map2.set_initial_value(moving_manipulator(mm2), False)
    map2.set_initial_value(moving_vacuum(mv2), False)

    # Grid connectivity
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

    rooms = [rm1, rm2, rm3, rm4, rm5, rm6, rm7, rm8, corridor]

    for r in rooms:
        map3.set_initial_value(clean(r), False)
        map3.set_initial_value(tidy(r), False)
        map3.set_initial_value(current_room_manipulator(mm3, r), False)
        map3.set_initial_value(current_room_vacuum(mv3, r), False)
        for r_other in rooms:
            map3.set_initial_value(connected(r, r_other), False)

    # Moving fluents start False
    map3.set_initial_value(moving_manipulator(mm3), False)
    map3.set_initial_value(moving_vacuum(mv3), False)

    # Robot starting positions
    map3.set_initial_value(current_room_manipulator(mm3, corridor), True)
    map3.set_initial_value(current_room_vacuum(mv3, corridor), True)

    # Room connectivity (corridor hub)
    for r in [rm1, rm2, rm3, rm4, rm5, rm6, rm7, rm8]:
        map3.set_initial_value(connected(corridor, r), True)
        map3.set_initial_value(connected(r, corridor), True)

    # Initial room states
    for r in [rm1, rm2, rm3, rm4]:
        map3.set_initial_value(tidy(r), True)   # tidy but not clean

    for r in [rm5, rm6, rm7, rm8]:
        map3.set_initial_value(clean(r), True)  # clean but not tidy

    map3.set_initial_value(clean(corridor), True)
    map3.set_initial_value(tidy(corridor), True)

    for r in [rm1, rm2, rm3, rm4, rm5, rm6, rm7, rm8]:
        map3.add_goal(clean(r))
        map3.add_goal(tidy(r))

    return map3


# ====================
# SOLVER
# ====================
from unified_planning.engines import PlanGenerationResultStatus

def solve(prob):
    with OneshotPlanner(name='tamer') as planner:
        result = planner.solve(prob)
        if result.status in [PlanGenerationResultStatus.SOLVED_SATISFICING,
                             PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
            print("SOLVED")
            for start, action, duration in result.plan.timed_actions:
                print(f"{float(start)}: {action} [{float(duration)}]")
        else:
            print("NOT SOLVED")

def solve_aries(prob):
    with OneshotPlanner(name='aries') as planner:
        result = planner.solve(prob)
        if result.status in [PlanGenerationResultStatus.SOLVED_SATISFICING,
                             PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
            print("SOLVED")
            for start, action, duration in result.plan.timed_actions:
                print(f"{float(start)}: {action} [{float(duration)}]")
        else:
            print("NOT SOLVED")


print("Map1")
solve(prob1())

print("\nMap2")
solve(prob2())

print("\nMap3")
solve_aries(prob3())