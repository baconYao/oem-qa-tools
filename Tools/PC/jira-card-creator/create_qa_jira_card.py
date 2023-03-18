import os
import json
import copy
from argparse import ArgumentParser

from pc_platform_tracker import generate_platform_tracker
from Jira.scenarios.pc.pc import create_task_card

# Get path of the configs of PC project from PC scenario in Jira API
project_conf_folders = os.path.join(
    os.getcwd(), "Jira", "scenarios", "pc", "configs")

if not os.path.exists(project_conf_folders):
    raise Exception("Fail to find the path of PC configs")

SUPPORTED_PROJECTS = [
    os.path.splitext(i)[0] for i in os.listdir(project_conf_folders)
    if os.path.splitext(i)[1] == ".json"
]


def combine_duplicate_tag(data, primary_key):
    for milestone, platform_data in data.items():
        needed_data = {}

        for platform in platform_data:
            tag = platform.pop(primary_key)
            platform_name = platform.pop("platform_name", "")
            new_name = platform_name.split("(")[0]

            # Put the platform_name into a list even though there's only one
            # record for this tag
            if milestone != "rts":
                platform.update({"platform_name": [new_name]})
                needed_data.update({tag: platform})
                continue

            if "product_name" not in platform.keys() or \
               platform_name == "":
                continue

            product_name = platform.pop("product_name")

            if tag in needed_data.keys():
                needed_data[tag]["platform_name"].append(new_name)
                if product_name is not None:
                    needed_data[tag]["product_name"].append(product_name)
            else:
                platform.update({"platform_name": [new_name]})
                if product_name is not None:
                    platform.update({"product_name": [product_name]})
                needed_data.update({tag: platform})

        new_data = []
        if needed_data:
            for tag, value in needed_data.items():
                value.update({primary_key: tag})
                new_data.append(value)

        data.update({milestone: new_data})

    return data


def register_arguments():
    options = copy.deepcopy(SUPPORTED_PROJECTS)
    options.append("all")

    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--project",
        help="select one of supported projects",
        type=str, required=True,
        choices=options,
    )
    return parser.parse_args()


def main():
    args = register_arguments()
    projects = SUPPORTED_PROJECTS if args.project == "all" else [args.project]
    payload = {}
    for project in projects:
        if project in ["stella", "sutton"]:
            primary_key = "lp_tag"
        else:
            # by default, we will group record by platform code name
            primary_key = "platform_tag"

        obj_pj_book = generate_platform_tracker(project)
        project_payload = obj_pj_book.dump_to_dict("status.eq=in-flight")
        new_payload = combine_duplicate_tag(project_payload, primary_key)
        if new_payload:
            payload.update({project: new_payload})

    if payload:
        print(json.dumps(payload, indent=4))
        create_task_card(payload)


if __name__ == "__main__":
    main()
