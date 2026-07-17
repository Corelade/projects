from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from app import backtrack, print_schedule, scheduler
from classes import *
import json
from prompt_toolkit import prompt
from typing import TypedDict


class DepartmentDict(TypedDict):
    department_name: str
    min_num_staff: int
    max_num_staff: int
    id: int | None


class StaffDict(TypedDict):
    name: str
    position: str
    shift_exclusion_list: list
    day_exclusion_list: list
    contract_hours: int
    id: int | None = None


load_dotenv()
import os

api_key = os.getenv("SHIFT_AI_KEY")
client = OpenAI(api_key=api_key)


def ai_scheduler(
    department_objects: list[DepartmentDict],
    staff_objects: list[StaffDict],
    use_id=False,
):
    try:
        departments = [DepartmentData(**dept) for dept in department_objects]
        staff = [StaffData(**staff) for staff in staff_objects]
    except Exception as e:
        return str(e)

    res = scheduler(departments, staff, use_id=use_id)
    # print_schedule(res)
    return json.dumps(res)


tools = [
    {
        "type": "function",
        "name": "ai_scheduler",
        "description": "A function for generating weekly schedules for shifts",
        "parameters": {
            "type": "object",
            "properties": {
                "departments": {
                    "type": "array",
                    "description": "A list containing all of the currently available departments",
                    "items": {
                        "type": "object",
                        "properties": {
                            "department_name": {
                                "type": "string",
                                "description": "The name of the department.",
                            },
                            "max_num_staff": {
                                "type": "integer",
                                "description": "The maximum number of staff that can be assigned to the departent at any given time.",
                            },
                            "min_num_staff": {
                                "type": "integer",
                                "description": "The minimum number of staff that can be assigned to the departent at any given time.",
                            },
                            "id": {
                                "type": ["integer", "null"],
                                "description": "Database identifier for this department.",
                            },
                        },
                        "required": ["department_name"],
                        "additionalProperties": False,
                    },
                },
                "staff": {
                    "type": "array",
                    "description": "A list containing all the currently available staff",
                    "items": {
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
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                },
                "use_id": {
                    "type": "boolean",
                    "description": "Whether staff members should be identified using their id or name.",
                },
            },
            "additionalProperties": False,
            "required": ["departments", "staff"],
        },
    }
]


def call_openai(input_list):
    response = client.responses.create(
        model="gpt-5.4",
        input=input_list,
        tools=tools,
    )

    return response


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
        input_list.extend(resp.output)
        for item in resp.output:
            if item.type == "function_call":
                arguments = json.loads(item.arguments)

                result = ai_scheduler(
                    department_objects=arguments["departments"],
                    staff_objects=arguments["staff"],
                    use_id=arguments.get("use_id", False),
                )

                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": result,
                    }
                )

                resp = call_openai(input_list)
                input_list.extend(resp.output)

        print(f"Bot: {resp.output_text}\n")


# async def call_openai():
#     print('asking ai')
#     response = await client.responses.create(
#         model="gpt-5.4", input="Write a one-sentence bedtime story about a unicorn."
#     )

#     print(response.output_text)


# async def delay_code():
#     print('delaying')
#     await asyncio.sleep(1)
#     response = requests.get("http://127.0.0.1:8000/")
#     resp = response.json()
#     print(resp)


# async def main():
#     await asyncio.gather(call_openai(), delay_code())


# asyncio.run(main())
