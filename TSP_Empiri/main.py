import pandas as pd
import time
import tsplib95
import os
from pyCombinatorial.algorithm import nearest_neighbour, christofides_algorithm, local_search_2_opt
from pyCombinatorial.utils import graphs, util

# variablen TSP_name er navnet på probleminstansen i TSPLib95 som skal hentes:
TSP_name = "pr107"
number_of_runs = 1
is_graph_displayed = False

TSP_library_file_path = os.path.join(os.getcwd(), "TSPLIB95/tsp")
TSP_problem_filepath = f"{TSP_library_file_path}/{TSP_name}.tsp"
TSP_problem_optimal_tour_filepath = f"{TSP_library_file_path}/{TSP_name}.opt.tour"

problem = tsplib95.load(TSP_problem_filepath)

if os.path.exists(TSP_problem_optimal_tour_filepath):
    problem_optimal_tour = tsplib95.load(TSP_problem_optimal_tour_filepath)

    optimal_tour_cost = problem.trace_tours(problem_optimal_tour.tours)
    print(f"\nOptimal tour distance of {problem.name}: {optimal_tour_cost[0]}\n")
else:
    print(f"File not found: {TSP_problem_optimal_tour_filepath}")

if hasattr(problem, 'node_coords'):
    node_coords = problem.node_coords

    coordinates_df = pd.DataFrame.from_dict(node_coords, orient='index', columns=['x', 'y'])

    output_folder = os.path.join(os.getcwd(), "output_coordinates")
    os.makedirs(output_folder, exist_ok=True)

    TSP_problem_csv_filepath = os.path.join(output_folder, f"{TSP_name}_output_coordinates.csv")

    if os.path.exists(TSP_problem_csv_filepath):
        print(f"The file '{TSP_problem_csv_filepath}' already exists. Skipping creation.")
    else:
        coordinates_df.to_csv(TSP_problem_csv_filepath, sep='\t', index=False)
        print(f"File saved at: {TSP_problem_csv_filepath}")
else:
    print("This TSPLIB file does not contain node coordinates.")

coordinates = pd.read_csv(TSP_problem_csv_filepath, sep = '\t')
coordinates = coordinates.values

# Obtaining the Distance Matrix
distance_matrix = util.build_distance_matrix(coordinates)

# NN - Parameters
parameters = {
            'initial_location': 1, # -1 =  Try All Locations.
            'local_search': False, 
            'verbose': False
             }

# NN - Algorithm
print('Runtime for Nearest Neighbor Algorithm with 2-opt:')
number_of_2_opt_iterations = -1
delimiter =";"
for i in range(number_of_runs):
    runtime_start = time.perf_counter()
    routeNN, distanceNN = nearest_neighbour(distance_matrix, **parameters)
    routeNN = [int(x) for x in routeNN]
    routeNN2Opt, distanceNN2Opt = local_search_2_opt(distance_matrix, [routeNN, distanceNN], recursive_seeding=number_of_2_opt_iterations, verbose=True)
    runtime_end = time.perf_counter()
    runtime_NNA_2_Opt = str(runtime_end - runtime_start).replace('.', ',')
    if (i == number_of_runs - 1):
        delimiter = ""
    print(runtime_NNA_2_Opt,end=delimiter)
distanceNNA2OptString = str(round(distanceNN2Opt, 2)).replace('.', ',')
print(f"\nTotal Distance for Nearest Neighbor Algorithm with 2-opt:\n{distanceNNA2OptString}")

# Christofides Algorithm - Algorithm
print('Runtime for Christofides algorithm:')
delimiter =";"
for i in range(number_of_runs):
    runtime_start = time.perf_counter()
    routeChr, distanceChr = christofides_algorithm(distance_matrix, local_search = False, verbose = False)
    runtime_end = time.perf_counter()
    runtime_Chr = str(runtime_end - runtime_start).replace('.', ',')  
    if (i == number_of_runs - 1):
        delimiter = ""
    print(runtime_Chr,end=delimiter)
distanceChrString = str(round(distanceChr, 2)).replace('.', ',')
print(f"\nTotal Distance for Christofides algorithm:\n{distanceChrString}")

# Plot Locations and Tour
if is_graph_displayed:
    graphs.plot_tour(coordinates, city_tour = routeNN2Opt, view = 'notebook', size = 10)
    graphs.plot_tour(coordinates, city_tour = routeChr, view = 'notebook', size = 5)

 