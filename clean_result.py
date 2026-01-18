

def clean_result(raw_result):
    failed_rules = []

    to_keep1= raw_result["report"]["jobs"][0]
    is_ok = to_keep1.get("validationResult")
    if is_ok :
        to_keep = to_keep1["validationResult"][0]["details"]["ruleSummaries"]
        for item in to_keep: 
            rule = {"ruleId": item["clause"], "description": item["description"]}
            failed_rules.append(rule)
    return failed_rules
