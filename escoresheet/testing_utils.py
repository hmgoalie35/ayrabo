"""
A module that contains useful methods for testing
"""


def get_messages(response):
    messages = []
    for msg in response.context['messages']:
        messages.append(msg.message)
    return messages
