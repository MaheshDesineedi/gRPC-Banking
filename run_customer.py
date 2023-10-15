import sys
import json
import time

import Customer as client


"""
    Create Customer Process and execute events
"""
def execute_customer_events(id, events):
    customer_obj = client.Customer(id, events)
    customer_obj.createStub()
    return customer_obj.executeEvents()


def main():
    # parse input json
    with open(sys.argv[1], 'r') as f:
        input_json = json.load(f)

    result_json = []
    for input in input_json:
        if input["type"] == "customer":

            id = int(input["id"])
            events = input["events"]

            event_results = execute_customer_events(id, events)

            res_json = dict()
            res_json["id"] = id
            res_json["recv"] = event_results

            result_json.append(res_json)

    for res in result_json:
        print(res)

    # write to file
    with open(r'./output/output.json', 'w') as fp:
        fp.write('[')
        fp.write(','.join(str(res).replace("\'", "\"") for res in result_json))
        fp.write(']')


if __name__ == "__main__":
    main()