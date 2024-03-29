
import argparse
import json


def sort_by_name_and_size(program):
    SIZES = {
        "MINI": 0,
        "SMALL": 1,
        "MEDIUM": 2,
        "LARGE": 3,
        "XLARGE": 4
    }
    name = program.split("_")[1]
    size = program.split("_")[-1]
    return name, SIZES[size]

parser = argparse.ArgumentParser()

parser.add_argument(
    "--results_schedules",
    default=""
)

parser.add_argument(
    "--original",
    default="results_generators"
)

parser.add_argument(
    "--schedules",
    default="schedules"
)


if __name__ == "__main__":
    args = parser.parse_args()

    if not args.results_schedules:
        args.results_schedules = f"results_{args.schedules}"

    # load the explored_programs.json from the schedules folder
    with open(f"{args.schedules}/explored_programs.json", "r") as f:
        explored_programs = json.load(f)
    for program in explored_programs:
        if args.original:    
            # read the execution times from the no-schedules folder
            with open(f"{args.original}/{program}.txt", "r") as f:
                results = f.read()
                results = [float(x) for x in results.split()]
                if results:
                    explored_programs[program]["original_min"] = min(results)
                    explored_programs[program]["original_all"] = results
        else:
            explored_programs[program]["original_min"] = None
            explored_programs[program]["original_all"] = None

        # read the execution times from the schedules folder
        with open(f"{args.results_schedules}/{program}.txt", "r") as f:
            results = f.read()
            results = [float(x) for x in results.split()]
            if results:
                explored_programs[program]["schedules_min"] = min(results)
                explored_programs[program]["schedules_all"] = results

    print("explored: ", len(explored_programs))
    # save dict as json and csv file
    with open(f"{args.schedules}_results.json", "w") as f:
        json.dump(explored_programs, f, indent=4)

    with open(f"{args.schedules}_results.csv", "w") as f:
        f.write(
            "program,schedule,original_min,schedules_min,speedup,speedup_predicted_model\n")
        sorted_names = list(explored_programs.keys())
        sorted_names.sort(key=sort_by_name_and_size)
        # print(len(sorted_names))
        for program in sorted_names:
            if not 'schedules_min' in explored_programs[program]:
                continue
            speedup = 1
            if explored_programs[program]['schedule']:
                speedup = explored_programs[program]['original_min'] / \
                    explored_programs[program]['schedules_min'] if explored_programs[program]['original_min'] else None
            f.write(
                f"{program},{explored_programs[program]['schedule'].replace(',',';')},{explored_programs[program]['original_min']},{explored_programs[program]['schedules_min']},{speedup},{explored_programs[program]['speedup_model']}\n")

        # filter explored_programs to only contain programs with schedules_min defined
        explored_programs_filtered = {program: explored_programs[program]
                                      for program in explored_programs
                                      if 'schedules_min' in explored_programs[program]}
        print([program for program in explored_programs if 'schedules_min' not in explored_programs[program]])
        # calculate the geomean of the speedups
        if not args.original:
            exit(0)

        speedups = [explored_programs_filtered[program]['original_min'] /
                    explored_programs_filtered[program]['schedules_min'] for program in explored_programs_filtered]
        speedups_model = [explored_programs_filtered[program]['speedup_model']
                          for program in explored_programs_filtered]

        geomean = 1
        geomean_model = 1

        for i in range(len(speedups)):
            geomean *= speedups[i]
            geomean_model *= speedups_model[i]

        geomean = geomean**(1/len(speedups))
        geomean_model = geomean_model**(1/len(speedups_model))
        f.write(f"geomean,,,,{geomean},{geomean_model}\n")

        # calculate the mean of the speedups
        mean = sum(speedups)/len(speedups)
        mean_model = sum(speedups_model)/len(speedups_model)
        f.write(f"mean,,,,{mean},{mean_model}\n")

        # calculate the median of the speedups
        speedups.sort()
        median = speedups[len(speedups)//2]
        speedups_model.sort()
        median_model = speedups_model[len(speedups_model)//2]
        f.write(f"median,,,,{median},{median_model}\n")

    print("done!")
