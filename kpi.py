import os 
import json 
mal_kpi = {}
ben_kpi = {}

def gen_kpi(resultsdir):
    global mal_kpi, ben_kpi
    for filename in os.listdir(resultsdir):
        if filename.endswith("_malicious_result.json"):
            filepath = os.path.join(resultsdir, filename)
            with open(filepath, "r") as f:
                result = json.load(f)
                for rule in result:
                    if not mal_kpi.get(rule["ruleId"]):
                        mal_kpi[rule["ruleId"]] = {"description": rule["description"], "time_hited": 1}
                    else : 
                        mal_kpi[rule["ruleId"]]["time_hited"] += 1
        elif filename.endswith("_benign_result.json"):
            filepath = os.path.join(resultsdir, filename)
            with open(filepath, "r") as f:
                result = json.load(f)
                for rule in result:
                    if not ben_kpi.get(rule["ruleId"]):
                        ben_kpi[rule["ruleId"]] = {"description": rule["description"], "time_hited": 1}
                    else : 
                        ben_kpi[rule["ruleId"]]["time_hited"] += 1


def save_kpi(kpi, outputpath):
    with open(outputpath, "w") as f:
        json.dump(kpi, f, indent=4) 