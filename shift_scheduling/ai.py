from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from app import scheduler, print_schedule, to_normal_dict, update_schedule
from classes import *
import json
from prompt_toolkit import prompt
from typing import TypedDict


class DepartmentDict(TypedDict):
    name: str
    min_staff: int
    max_staff: int
    id: int | None


class StaffDict(TypedDict):
    name: str
    position: str
    shift_exclusion_list: list
    day_exclusion_list: list
    contract_hours: int
    min_hours: int
    id: int | None = None


departmentSchema = {
    "type": "object",
    # "description": "A list containing all of the currently available departments",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of the department.",
        },
        "max_staff": {
            "type": "integer",
            "description": "The maximum number of staff that can be assigned to the departent at any given time.",
            "default": 1,
        },
        "min_staff": {
            "type": "integer",
            "description": "The minimum number of staff that can be assigned to the departent at any given time.",
            "default": 1,
        },
        "id": {
            "type": ["integer", "null"],
            "description": "Database identifier for this department.",
        },
    },
    "required": ["name"],
    "additionalProperties": False,
}

staffSchema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The name of staff",
        },
        "id": {
            "type": ["integer", "null"],
            "description": "Database identifier for this staff.",
        },
        "position": {
            "type": "string",
            "description": "The position of staff in the company.",
            "enum": [
                "associate",
            ],
            "default": "associate",
        },
        "shift_exclusion_list": {
            "type": "array",
            "description": "The shifts this staff member cannot work. Leave empty if the staff member has no shift restrictions.",
            "items": {
                "type": "string",
                "enum": [
                    "morning",
                    "afternoon",
                    "evening",
                ],
            },
            "default": [],
        },
        "day_exclusion_list": {
            "type": "array",
            "description": "The days this staff member cannot work. Leave empty if the staff member has no shift restrictions.",
            "items": {
                "type": "string",
                "enum": [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ],
            },
            "default": [],
        },
        "contract_hours": {
            "type": "integer",
            "description": "The number of hours this staff can work in a week. Shouldn't be more than 40",
            "default": 40,
        },
        "min_hours": {
            "type": "integer",
            "description": "The minimum number of hours this staff can work in a week. Shouldn't be more than contract hours",
            "default": 8,
        },
    },
    "required": ["name"],
    "additionalProperties": False,
}


load_dotenv()
import os

api_key = os.getenv("SHIFT_AI_KEY")
client = OpenAI(api_key=api_key)

departments = DepartmentData.list_departments()
staff_members = StaffData.list_staff_members()
assignment = {}


def create_department(
    department_objects: list[DepartmentDict] | DepartmentDict,
):
    try:
        if isinstance(department_objects, dict):
            department_objects = [department_objects]
        departments = [DepartmentData(**dept) for dept in department_objects]
        department_json = [
            {
                "name": dept.name,
                "min_staff": dept.min_staff,
                "max_staff": dept.max_staff,
                "id": dept.id,
            }
            for dept in departments
        ]
        return department_json
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_staff(
    staff_objects: list[StaffDict] | StaffDict,
):
    try:
        if isinstance(staff_objects, dict):
            staff_objects = [staff_objects]
        staff = [StaffData(**staff) for staff in staff_objects]
        staff_json = [
            {
                "name": stf.name,
                "position": stf.position,
                "contract_hours": stf.contract_hours,
                "min_hours": stf.min_hours,
                "id": stf.id,
            }
            for stf in staff
        ]
        return staff_json
    except Exception as e:
        return json.dumps({"error": str(e)})


def ai_scheduler():

    res = scheduler(departments, staff_members)
    if res:
        global assignment
        assignment = res
        # print_schedule(res)
        return json.dumps(to_normal_dict(res))
    return json.dumps({"error": "Unable to generate schedule"})


def ai_update_scheduler():
    updated_schedule = update_schedule(assignment, departments, staff_members)
    if updated_schedule:
        return json.dumps(to_normal_dict(updated_schedule))
    return json.dumps({"error": "Unable to update schedule"})


tools = [
    {
        "type": "function",
        "name": "create_department",
        "description": "A function for creating departments.",
        "parameters": {
            "type": "object",
            "properties": {
                "department_objects": {
                    "oneOf": [
                        departmentSchema,
                        {"type": "array", "items": departmentSchema},
                    ]
                },
            },
            "additionalProperties": False,
            "required": ["department_objects"],
        },
    },
    {
        "type": "function",
        "name": "create_staff",
        "description": "A function for creating staff.",
        "parameters": {
            "type": "object",
            "properties": {
                "staff_objects": {
                    "oneOf": [
                        staffSchema,
                        {"type": "array", "items": staffSchema},
                    ]
                },
            },
            "additionalProperties": False,
            "required": ["staff_objects"],
        },
    },
    {
        "type": "function",
        "name": "ai_scheduler",
        "description": "A function for generating weekly schedules for shifts. Do not attempt to manually create the schedule",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "ai_update_scheduler",
        "description": "A function for updating weekly shift schedules",
        "parameters": {
            "type": "object",
            "properties": {
                # "assignment": {
                #     "type": "object",
                #     "description": "The schedule to update",
                #     "additionalProperties": {
                #         "type": "object",
                #         "additionalProperties": {
                #             "type": "object",
                #             "additionalProperties": {
                #                 "type": "array",
                #                 "items": {
                #                     "type": "string",
                #                 },
                #             },
                #         },
                #     },
                # },
                # "departments": {
                #     "type": "array",
                #     "items": {
                #         "type": departmentSchema,
                #     },
                # },
                # "staff": {
                #     "type": "array",
                #     "items": {
                #         "type": staffSchema,
                #     },
                # },
            },
            "additionalProperties": False,
            "required": [],
        },
    },
]


def call_openai(input_list):
    response = client.responses.create(
        model="gpt-5.4",
        input=input_list,
        tools=tools,
    )

    return response


tool_functions = {
    "create_department": create_department,
    "create_staff": create_staff,
    "ai_scheduler": ai_scheduler,
}


input_list = []
if __name__ == "__main__":
    while True:
        question = prompt("\nUser: ")
        input_list.append(
            {
                "role": "user",
                "content": question,
            }
        )
        resp = call_openai(input_list)

        while True:
            input_list.extend(resp.output)
            tool_called = False
            for item in resp.output:
                if item.type == "function_call":
                    tool_called = True

                    function = tool_functions[item.name]
                    arguments = json.loads(item.arguments)

                    result = function(**arguments)

                    input_list.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps(result),
                        }
                    )

            if not tool_called:
                break

            resp = call_openai(input_list)
            # input_list.extend(resp.output)

        print(f"Bot: {resp.output_text}\n")
