import uuid


def generate_unique_string(length=10):
    # Generate a UUID (Universally Unique Identifier)
    unique_id = uuid.uuid4().hex
    # Extract alphanumeric characters
    alphanumeric = ''.join(char for char in unique_id if char.isalnum())
    # Ensure the string length is not greater than specified length
    return alphanumeric[:length]

