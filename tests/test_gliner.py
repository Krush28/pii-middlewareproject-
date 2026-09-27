from gliner2 import GLiNER2

# Load the GLiNER2 model
model = GLiNER2.from_pretrained("fastino/gliner2-base-v1")

# Text we want to analyze
text = """
My name is Rahul Sharma.
My email is rahul@gmail.com.
My phone number is 9876543210.
I work at ABC Technologies.
My employee ID is EMP1024.
"""

# Tell GLiNER2 what entities we want to find
entities = [
    "person",
    "email address",
    "phone number",
    "organization",
    "employee ID",
]

# Extract entities
result = model.extract_entities(text, entities)

print("\n========== RESULT ==========\n")
print(result)