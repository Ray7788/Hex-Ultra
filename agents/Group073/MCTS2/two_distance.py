def egde_coordinates_generator(state):
    possible_actions = state.getPossibleActions()
    # whole_board_test_red = [(0,1),(1,1),(0,10), (1,10)]
    # whole_board_test_blue = [(0,1),(0,2),(10,1),(10,2)]
    # # for i in range(10):
    # #         whole_board.append((10, i))
    # possible_actions = whole_board_test_blue
    # for blue
    # the edges are the first 11 coordinates in possible_actions
    if len(possible_actions) > 11:
        lower_egde_coordinates_blue = possible_actions[0:11]
        upper_egde_coordinates_blue = possible_actions[::-1][0:11][::-1]
    else:
        lower_egde_coordinates_blue = possible_actions
        upper_egde_coordinates_blue = sorted(possible_actions, key=lambda x: (-x[0]))
    # for red
    if len(possible_actions) > 11:
        lower_egde_coordinates_red = sorted(possible_actions, key=lambda x: x[1])[0:11]
        upper_egde_coordinates_red = sorted(possible_actions, key=lambda x: x[1])[::-1][0:11][::-1]
    else:
        lower_egde_coordinates_red = sorted(possible_actions, key=lambda x: x[1])
        upper_egde_coordinates_red = sorted(possible_actions, key=lambda x: (-x[1]))
    return lower_egde_coordinates_blue, upper_egde_coordinates_blue, lower_egde_coordinates_red, upper_egde_coordinates_red


# find_neighbours in possible coordinates
def find_neighbours(tile_coordinates, distance_dict):
    board_size = 11
    num_neighbours = 6
    i_displacements = [-1, -1, 0, 1, 1, 0]
    j_displacements = [0, 1, 1, 0, -1, -1]
    neighbours = []
    # find 6 neighbours or less if there are less than 6 possible coordinates
    if len(distance_dict.keys()) > 6:
        for i in range(num_neighbours):
            # 我们能加进neighbours的coordinates都必须是在这一round被visted过的，所以查在不在distancec_dict里面。在之前的turns被选过的cell并不会在distance——dict里面，并且可能是tile的default neighbours，所以需要调整tile的neighbours
            x = tile_coordinates[0] + i_displacements[i]
            y = tile_coordinates[1] + j_displacements[i]
            if 0 <= x < board_size and 0 <= y < board_size:
                if (x, y) in distance_dict:
                    neighbours.append((x, y))
                else:
                    list_of_closest_cooridnates = []
                    min_distance = float("inf")
                    for coordinate in distance_dict.keys():
                        value = int((x - coordinate[0]) ** 2 + (y - coordinate[1]) ** 2)
                        if value < min_distance:
                            list_of_closest_cooridnates.clear()
                            list_of_closest_cooridnates.append(coordinate)
                            min_distance = value
                        elif value == min_distance:
                            list_of_closest_cooridnates.append(coordinate)
                    cloest_coordinate = min(list_of_closest_cooridnates, key=lambda x: distance_dict[x])
                    if cloest_coordinate not in neighbours:
                        neighbours.append(cloest_coordinate)
    else:
        neighbours = distance_dict.keys()
    return neighbours


# The two-distance is one more than the d value
def two_distance(p, distance_dict, edge_coordinates):
    if p in edge_coordinates:
        return 1
    else:
        neighbour_distance_list = []
        for r in find_neighbours(p, distance_dict):
            r_distance = distance_dict[r]
            neighbour_distance_list.append(r_distance)
        neighbour_distance_list_sorted = sorted(neighbour_distance_list)
        # do not remove duplicates in distance list to get the real second-lowest distance
        if len(neighbour_distance_list_sorted) == 1:
            return neighbour_distance_list_sorted[0] + 1
        else:
            return neighbour_distance_list_sorted[1] + 1


def forming_distance_board(state, distance_board_lower_blue, distance_board_upper_blue, distance_board_lower_red,
                           distance_board_upper_red):
    possible_coordinates = state.getPossibleActions()

    lower_egde_coordinates_blue, upper_egde_coordinates_blue, lower_egde_coordinates_red, upper_egde_coordinates_red = egde_coordinates_generator(
        state)

    # for blue
    for coordinate in possible_coordinates:
        distance_board_lower_blue[coordinate] = two_distance(coordinate, distance_board_lower_blue,
                                                             lower_egde_coordinates_blue)
    for coordinate in sorted(possible_coordinates, key=lambda x: (-x[0])):
        distance_board_upper_blue[coordinate] = two_distance(coordinate, distance_board_upper_blue,
                                                             upper_egde_coordinates_blue)

    # for red
    for coordinate in sorted(possible_coordinates, key=lambda x: x[1]):
        distance_board_lower_red[coordinate] = two_distance(coordinate, distance_board_lower_red,
                                                            lower_egde_coordinates_red)

    for coordinate in sorted(possible_coordinates, key=lambda x: (-x[1])):
        distance_board_upper_red[coordinate] = two_distance(coordinate, distance_board_upper_red,
                                                            upper_egde_coordinates_red)
    return distance_board_lower_blue, distance_board_upper_blue, distance_board_lower_red, distance_board_upper_red


def check_attack_mobility(state, actions):
    attack_mobility_blues = {}
    attack_mobility_reds = {}
    for action in actions:
        # check the attack mobility for blue and red after taking this action
        next_state = state.takeAction(action)
        distance_board_lower_blue = {}
        distance_board_upper_blue = {}
        distance_board_lower_red = {}
        distance_board_upper_red = {}
        distance_board_lower_blue, distance_board_upper_blue, distance_board_lower_red, distance_board_upper_red = forming_distance_board(
            next_state, distance_board_lower_blue, distance_board_upper_blue, distance_board_lower_red,
            distance_board_upper_red)
        potential_board_blue = {}
        potential_board_red = {}
        for coordinate in distance_board_lower_blue.keys():
            potential_board_blue[coordinate] = distance_board_lower_blue[coordinate] + distance_board_upper_blue[
                coordinate]
        for coordinate in distance_board_lower_red.keys():
            potential_board_red[coordinate] = distance_board_lower_red[coordinate] + distance_board_upper_red[
                coordinate]
        min_value_blue = min(potential_board_blue.values())
        min_value_red = min(potential_board_red.values())
        keys_with_min_value_blue = [key for key, value in potential_board_blue.items() if value == min_value_blue]
        keys_with_min_value_red = [key for key, value in potential_board_red.items() if value == min_value_red]
        attack_mobility_blue = len(keys_with_min_value_blue)
        attack_mobility_red = len(keys_with_min_value_red)
        attack_mobility_blues[action] = attack_mobility_blue
        attack_mobility_reds[action] = attack_mobility_red
    return attack_mobility_blues, attack_mobility_reds


def potential(state):
    while not state.isTerminal():
        try:
            player = state.getCurrentPlayer()
            # print(state.getCurrentPlayer())
            distance_board_lower_blue = {}
            distance_board_upper_blue = {}
            distance_board_lower_red = {}
            distance_board_upper_red = {}
            distance_board_lower_blue, distance_board_upper_blue, distance_board_lower_red, distance_board_upper_red = forming_distance_board(
                state, distance_board_lower_blue, distance_board_upper_blue, distance_board_lower_red,
                distance_board_upper_red)
            potential_board_blue = {}
            potential_board_red = {}

            for coordinate in distance_board_lower_blue.keys():
                potential_board_blue[coordinate] = distance_board_lower_blue[coordinate] + distance_board_upper_blue[
                    coordinate]
            for coordinate in distance_board_lower_red.keys():
                potential_board_red[coordinate] = distance_board_lower_red[coordinate] + distance_board_upper_red[
                    coordinate]

            # print("potential_board_blue", potential_board_blue)
            # print("potential_board_red", potential_board_red)
            # Find the minimum value in the dictionary
            # min_value_blue = min(potential_board_blue.values())
            # min_value_red = min(potential_board_red.values())

            potential_board_e = {}
            # 1. 先考虑 e 值
            # attack_mobility_blues, attack_mobility_reds = check_attack_mobility(state, distance_board_lower_blue.keys())
            # M = 100
            # for coordinate in distance_board_lower_blue.keys():
            #     if player == 1:
            #         e = (M * (potential_board_blue[coordinate] - potential_board_red[coordinate])) - (
            #                 attack_mobility_blues[coordinate] - attack_mobility_reds[coordinate])
            #         potential_board_e = potential_board_blue
            #     else:
            #         e = M * (potential_board_red[coordinate] - potential_board_blue[coordinate]) - (
            #                 attack_mobility_reds[coordinate] - attack_mobility_blues[coordinate])
            #     potential_board_e[coordinate] = e
            if player == 1:
                potential_board_e = potential_board_blue
            else:
                potential_board_e = potential_board_red
            # find the keys with minimum value in potential_board_e
            min_value_e = min(potential_board_e.values())
            keys_with_min_value_e = [key for key, value in potential_board_e.items() if value == min_value_e]
            if len(keys_with_min_value_e) == 1:
                action = keys_with_min_value_e[0]
            else:
                # 2. 再考虑 blue p + red p
                potential_board_sum = {}
                for coordinate in keys_with_min_value_e:
                    potential_board_sum[coordinate] = potential_board_blue[coordinate] + potential_board_red[coordinate]
                # find the keys with minimum value in potential_board_sum
                min_value_sum = min(potential_board_sum.values())
                keys_with_potential_board_sum = [key for key, value in potential_board_sum.items() if
                                                     value == min_value_sum]
                # print("keys_with_potential_board_sum", keys_with_potential_board_sum)
                if len(keys_with_potential_board_sum) == 1:
                    action = keys_with_potential_board_sum[0]

                elif len(keys_with_potential_board_sum) > 1:
                    # 3. 再考虑 attack mobility
                    attack_mobility_blues_filtered, attack_mobility_reds_filtered = check_attack_mobility(state, keys_with_potential_board_sum)
                    # print("attack_mobility_blues_filtered", attack_mobility_blues_filtered)
                    # print("attack_mobility_reds_filtered", attack_mobility_reds_filtered)
                    if player == 1:
                        max_blue = max(attack_mobility_blues_filtered.values())
                        max_blue_actions = [key for key, value in attack_mobility_blues_filtered.items() if value == max_blue]
                        red_values = [attack_mobility_reds_filtered[key] for key in max_blue_actions]
                        action = max_blue_actions[red_values.index(min(red_values))]
                    else:
                        max_red = max(attack_mobility_reds_filtered.values())
                        max_red_actions = [key for key, value in attack_mobility_reds_filtered.items() if value == max_red]
                        blue_values = [attack_mobility_blues_filtered[key] for key in max_red_actions]
                        action = max_red_actions[blue_values.index(min(blue_values))]
            # print("action",action)
            # else:
            #     action = max(potential_board_combine, key=lambda k: potential_board_combine[k])
            #     print("action",action)
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
    # print("state.getReward()", state.getReward())
    return state.getReward()
