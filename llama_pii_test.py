import time
import json
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"

MAX_NEW_TOKENS = 256

# CPU only
DEVICE = "cpu"


# ============================================================
# STARTUP
# ============================================================

print("=" * 70)
print("LLAMA PII DETECTION TEST")
print("=" * 70)

print(f"PyTorch version: {torch.__version__}")
print(f"Device: {DEVICE}")
print(f"Model: {MODEL_NAME}")

print("\n" + "=" * 70)
print("Loading tokenizer...")
print("=" * 70)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

print("Tokenizer loaded successfully.")


# ============================================================
# LOAD MODEL
# ============================================================

print("\n" + "=" * 70)
print("Loading model...")
print("=" * 70)

start_time = time.time()

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
)

# IMPORTANT:
# Do NOT use device_map="auto" here.
# We are running on CPU.
model = model.to(DEVICE)

model.eval()

load_time = time.time() - start_time

print(f"Model loaded successfully in {load_time:.2f} seconds.")
print("Device:", next(model.parameters()).device)


# ============================================================
# PII TYPES
# ============================================================

PII_TYPES = [
    "PERSON",
    "EMAIL",
    "PHONE",
    "ADDRESS",
    "DATE_OF_BIRTH",
    "CUSTOMER_ID",
    "EMPLOYEE_ID",
    "PASSPORT",
    "DRIVER_LICENSE",
    "NATIONAL_ID",
    "ORGANIZATION",
    "JOB_TITLE"
]


# ============================================================
# PII EXTRACTION FUNCTION
# ============================================================

def extract_pii(text):
    """
    Send text to Llama and ask for PII entities.

    The model must return JSON in this format:

    {
        "entities": [
            {
                "type": "PERSON",
                "value": "Aarav Mehta"
            }
        ]
    }
    """

    system_prompt = """
You are a PII extraction system.

Your ONLY task is to identify personally identifiable information
that ACTUALLY APPEARS in the input text.

Do NOT invent information.

Do NOT use information from examples.

Do NOT use information from previous requests.

Do NOT guess missing values.

Every returned value MUST appear literally in the input text.

Return ONLY valid JSON.

The JSON format must be:

{
  "entities": [
    {
      "type": "PERSON",
      "value": "exact value from input"
    }
  ]
}

Allowed entity types:

PERSON
EMAIL
PHONE
ADDRESS
DATE_OF_BIRTH
CUSTOMER_ID
EMPLOYEE_ID
PASSPORT
DRIVER_LICENSE
NATIONAL_ID
ORGANIZATION
JOB_TITLE

If there is no PII, return:

{
  "entities": []
}
"""

    user_prompt = f"""
INPUT TEXT:

{text}

Remember:
Only extract information that is literally present in the INPUT TEXT.
Do not invent names, emails, phone numbers, addresses, or IDs.
Return JSON only.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    print("\nGenerating PII results...")

    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=None,
            pad_token_id=tokenizer.eos_token_id
        )

    generation_time = time.time() - start_time

    # Only decode newly generated tokens
    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    print(f"Generation time: {generation_time:.2f} seconds")

    print("\n" + "=" * 70)
    print("RAW MODEL RESPONSE")
    print("=" * 70)

    print(response)

    return parse_and_validate_response(response, text)


# ============================================================
# PARSE JSON
# ============================================================

def parse_and_validate_response(response, original_text):
    """
    Parse model JSON and remove hallucinated values.

    A value is accepted only if it occurs in the original input.
    """

    response = response.strip()

    # Remove markdown code fences if the model creates them
    response = re.sub(
        r"```json\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"```\s*",
        "",
        response
    )

    # Find the JSON object
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:
        print("\nCould not find valid JSON in model response.")

        return {
            "entities": []
        }

    json_text = response[start:end + 1]

    try:
        result = json.loads(json_text)

    except json.JSONDecodeError as error:
        print("\nJSON parsing error:")
        print(error)

        return {
            "entities": []
        }

    if not isinstance(result, dict):
        return {
            "entities": []
        }

    entities = result.get("entities", [])

    if not isinstance(entities, list):
        return {
            "entities": []
        }

    validated_entities = []

    for entity in entities:

        if not isinstance(entity, dict):
            continue

        entity_type = entity.get("type")
        value = entity.get("value")

        if not isinstance(entity_type, str):
            continue

        if not isinstance(value, str):
            continue

        entity_type = entity_type.strip().upper()
        value = value.strip()

        # Check entity type
        if entity_type not in PII_TYPES:
            print(
                f"Rejected unknown entity type: {entity_type}"
            )
            continue

        # Empty value
        if not value:
            continue

        # ====================================================
        # CRITICAL HALLUCINATION CHECK
        # ====================================================

        if value not in original_text:
            print(
                f"REJECTED HALLUCINATED VALUE: "
                f"{entity_type} -> {value}"
            )
            continue

        validated_entities.append(
            {
                "type": entity_type,
                "value": value
            }
        )

    # Remove duplicates
    unique_entities = []

    seen = set()

    for entity in validated_entities:

        key = (
            entity["type"],
            entity["value"]
        )

        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)

    return {
        "entities": unique_entities
    }


# ============================================================
# DISPLAY RESULTS
# ============================================================

def print_results(result):

    print("\n" + "=" * 70)
    print("FINAL VALIDATED PII RESULTS")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\n" + "=" * 70)
    print(f"TOTAL PII ENTITIES: {len(result['entities'])}")
    print("=" * 70)

    for entity in result["entities"]:

        print(
            f"{entity['type']:20} -> {entity['value']}"
        )


# ============================================================
# TEST DATA
# ============================================================

TEST_TEXT = """
My name is Aarav Mehta. I was born on 14 March 1992.
My email address is aarav.mehta@example.com.
My phone number is +91 90000 12345.
I live at 42 Palm Grove Road, Panaji, Goa 403001, India.

My customer ID is CUS-104582 and my employee ID is EMP-7821.
I work as a Software Engineer at Blue Horizon Technologies Pvt. Ltd.

My passport number is P0000001.
My driver's license number is DL-XX-000001.

My emergency contact is Priya Mehta.
Her phone number is +91 90000 12346.
"""


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("TEST INPUT")
    print("=" * 70)

    print(TEST_TEXT)

    result = extract_pii(TEST_TEXT)

    print_results(result)

    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)