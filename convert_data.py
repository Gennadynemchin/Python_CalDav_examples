import re


def from_byte_to_dict(tracker_data: bytes) -> dict:
    decoded_string = tracker_data.decode('utf-8')
    corrected_string = re.sub(r'(\w+@\w+\.\w+)', r'"\1"', decoded_string)
    output_data = eval(corrected_string)
    return output_data


if __name__ == "__main__":
    from_byte_to_dict(
                        b'{"attendees": [test1@test.ru, test2@test.ru],\
                        "deadline": "2027-08-29",\
                        "summary": "Title of task",\
                        "description": "Description of task"}'
                    )
