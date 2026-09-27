# PII Middleware Project

A privacy-focused middleware system for detecting, sanitizing, and protecting
Personally Identifiable Information (PII) before user data is sent to an
external Large Language Model (LLM).

The project is designed around a middleware architecture that sits between
an application and an LLM such as GPT.

The middleware detects sensitive information, replaces detected values with
stable placeholders, sends only sanitized text to the LLM, and restores the
original values when the response is returned to the application.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Project Objective](#project-objective)
- [Architecture](#architecture)
- [Complete Data Flow](#complete-data-flow)
- [Detection Layer](#detection-layer)
- [Microsoft Presidio](#microsoft-presidio)
- [Llama](#llama)
- [Detection Merger](#detection-merger)
- [Sanitization Policy](#sanitization-policy)
- [Placeholder Engine](#placeholder-engine)
- [LLM/GPT Layer](#llmgpt-layer)
- [Placeholder Restoration](#placeholder-restoration)
- [Example](#example)
- [Security Principle](#security-principle)
- [Current Implementation](#current-implementation)
- [Current Llama Test](#current-llama-test)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development Environment](#development-environment)
- [Installation](#installation)
- [Running the Current Llama Test](#running-the-current-llama-test)
- [Future Implementation](#future-implementation)
- [Testing Strategy](#testing-strategy)
- [Known Limitations](#known-limitations)
- [Security Considerations](#security-considerations)
- [Development Status](#development-status)
- [Future Goals](#future-goals)

---

# Overview

Modern applications increasingly send user-generated text to external LLM
services for processing.

User messages may contain sensitive information such as:

- Names
- Email addresses
- Phone numbers
- Physical addresses
- Customer IDs
- Employee IDs
- Passport numbers
- Driver's license numbers
- Account identifiers
- IP addresses
- Dates
- Locations
- Financial information
- Other organization-specific identifiers

Sending such information directly to an external LLM may create privacy and
data-protection concerns.

This project introduces a middleware layer that processes the information
before it reaches the LLM.

The intended principle is:

> Detect sensitive information first, sanitize it before the LLM request,
> and restore it only when necessary after the LLM response.

---

# Problem Statement

Consider an application sending the following request:

```text
My name is Aarav Mehta.
My email is aarav.mehta@example.com.
My customer ID is CUS-104582.

Sending the original request directly to an external LLM means that the LLM
receives the user's personal information.

The middleware instead transforms the request into:

My name is <<PII_PERSON_001>>.
My email is <<PII_EMAIL_001>>.
My customer ID is <<PII_CUSTOMER_ID_001>>.

The LLM receives only the sanitized representation.

The middleware maintains the mapping between the placeholders and the original
values.

Project Objective

The primary objectives of this project are:

Detect PII from application input.
Combine rule-based and model-based detection.
Validate detected entities.
Reduce false positives and duplicate detections.
Replace sensitive values with placeholders.
Prevent original PII from being sent to an external LLM.
Allow the LLM to operate on sanitized text.
Restore placeholders in the final response when required.
Measure detection and processing performance.
Provide a reusable middleware architecture for LLM applications.
Architecture

The intended architecture is:

                         +----------------------+
                         |  YOUR APPLICATION    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |    PII MIDDLEWARE    |
                         +----------+-----------+
                                    |
                  +-----------------+-----------------+
                  |                                   |
                  v                                   v
        +-------------------+              +-------------------+
        | Microsoft Presidio|              | Llama 3.2 1B      |
        |                   |              | Instruct           |
        | PII Detection     |              | Context Detection |
        +---------+---------+              +---------+---------+
                  |                                  |
                  +----------------+-----------------+
                                   |
                                   v
                         +----------------------+
                         |  DETECTION MERGER    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | SANITIZATION POLICY  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | PLACEHOLDER ENGINE   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |    SANITIZED TEXT    |
                         +----------+-----------+
                                    |
                                    v
                              +-----------+
                              |    GPT     |
                              |    / LLM   |
                              +-----+-----+
                                    |
                                    v
                         +----------------------+
                         | SANITIZED RESPONSE   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | PLACEHOLDER RESTORER |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |  YOUR APPLICATION    |
                         +----------------------+
Complete Data Flow

The middleware follows this general sequence:

1. Application creates request
              |
              v
2. Middleware receives request
              |
              v
3. Presidio detects PII
              |
              v
4. Llama performs contextual/custom detection
              |
              v
5. Detection results are merged
              |
              v
6. Duplicates and overlaps are resolved
              |
              v
7. Sanitization policy is applied
              |
              v
8. PII is replaced by placeholders
              |
              v
9. Sanitized text is sent to the LLM
              |
              v
10. LLM generates response
              |
              v
11. Placeholder restoration is performed
              |
              v
12. Final response is returned to application
Detection Layer

The detection layer is designed around two complementary approaches.

1. Microsoft Presidio

Presidio provides structured PII recognition using predefined recognizers
and patterns.

It is intended to handle common PII types reliably.

Examples include:

PERSON
EMAIL
PHONE
LOCATION
DATE
IP_ADDRESS
IBAN
BANK INFORMATION

and other supported entities.

2. Llama

Llama is being evaluated as a contextual detection component.

The purpose of the Llama component is to identify information that may require
contextual understanding or organization-specific entity recognition.

Examples include:

CUSTOMER_ID
EMPLOYEE_ID
TICKET_ID
ACCOUNT_ID
ORGANIZATION
JOB_TITLE

The model can also identify conventional PII such as names, emails, phone
numbers, addresses, and identification numbers.

The two detection systems are intended to complement each other rather than
replace one another.

Microsoft Presidio

Microsoft Presidio is an important part of the detection architecture.

Presidio is intended to provide the primary structured PII detection layer.

For example, given:

My email is aarav.mehta@example.com.
My phone is +91 90000 12345.

Presidio may produce detections similar to:

EMAIL  -> aarav.mehta@example.com
PHONE  -> +91 90000 12345

Presidio detections contain information such as:

Entity type
Detected value
Start position
End position
Confidence score
Recognizer

These results are then passed to the middleware's detection-merging layer.

Llama

The current local model being tested is:

meta-llama/Llama-3.2-1B-Instruct

The model is currently being tested locally using PyTorch and Hugging Face
Transformers.

The model is intended to provide contextual entity extraction.

A simplified request to the model asks it to return structured JSON:

{
  "entities": [
    {
      "type": "PERSON",
      "value": "Aarav Mehta"
    },
    {
      "type": "EMAIL",
      "value": "aarav.mehta@example.com"
    }
  ]
}

The system prompt instructs the model that:

It must only extract information present in the input.
It must not invent values.
It must not use previous information.
It must return structured JSON.
Entity values must appear literally in the input.
Llama Output Validation

Because generative models can produce malformed or unexpected output, the
current Llama test includes validation.

A returned entity is accepted only when:

The entity is an object.
The entity contains a valid type.
The entity contains a string value.
The entity type belongs to the allowed entity list.
The value is not empty.
The value literally exists in the original input.
Duplicate entities are removed.

The literal-value check is particularly important.

For example, if Llama produces:

{
  "type": "PERSON",
  "value": "Rahul Sharma"
}

but "Rahul Sharma" does not appear in the original input, the middleware
rejects the result.

This provides a basic hallucination safeguard.

Detection Merger

The Detection Merger combines the results from Presidio and Llama.

For example:

Presidio:

PERSON -> Aarav Mehta
EMAIL  -> aarav.mehta@example.com

Llama:

PERSON -> Aarav Mehta
EMAIL  -> aarav.mehta@example.com
CUSTOMER_ID -> CUS-104582

The merger should produce:

PERSON       -> Aarav Mehta
EMAIL        -> aarav.mehta@example.com
CUSTOMER_ID  -> CUS-104582

rather than sending duplicate detections into the sanitization layer.

The merger is intended to handle:

Duplicate detections
Overlapping spans
Different entity labels
Confidence scores
Detector source
Entity normalization
Priority rules
Sanitization Policy

Detection and sanitization are separate concepts.

A detector may identify something as potentially sensitive, but the middleware
must decide whether that entity should actually be replaced.

The sanitization policy will determine:

Which entity types are sanitized
Which confidence thresholds are accepted
How conflicting detections are handled
How overlapping detections are resolved
Which application-specific identifiers require protection

For example:

PERSON       -> sanitize
EMAIL        -> sanitize
PHONE        -> sanitize
CUSTOMER_ID  -> sanitize
TICKET_ID    -> sanitize

The policy can be extended according to the application's requirements.

Placeholder Engine

The Placeholder Engine replaces detected PII with stable placeholders.

Example:

Original:

My name is Aarav Mehta.
My email is aarav.mehta@example.com.

Sanitized:

My name is <<PII_PERSON_001>>.
My email is <<PII_EMAIL_001>>.

The middleware maintains a mapping similar to:

<<PII_PERSON_001>>
    ->
Aarav Mehta

<<PII_EMAIL_001>>
    ->
aarav.mehta@example.com

The original values remain inside the middleware's controlled context.

Why Placeholders?

Instead of simply deleting PII, placeholders preserve the semantic structure
of the message.

For example, deleting PII:

My name is .
My email is .

loses information about what the sentence means.

Using placeholders:

My name is <<PII_PERSON_001>>.
My email is <<PII_EMAIL_001>>.

allows the LLM to understand the structure of the request while preventing it
from receiving the original values.

LLM/GPT Layer

The external LLM should receive only sanitized text.

Example:

Original:

My customer ID is CUS-104582.
Please check my account.

The LLM request becomes:

My customer ID is <<PII_CUSTOMER_ID_001>>.
Please check my account.

The original customer ID is not included in the LLM request.

The LLM can therefore process the semantic content without requiring access
to the original sensitive value.

Placeholder Restoration

After the LLM produces a response, the middleware can restore placeholders.

Example LLM response:

Hello <<PII_PERSON_001>>.

Your request regarding <<PII_CUSTOMER_ID_001>>
has been received.

The middleware restores:

Hello Aarav Mehta.

Your request regarding CUS-104582
has been received.

The restored response is then returned to the application.

Example
Original Request
My name is Aarav Mehta.
My email is aarav.mehta@example.com.
My phone number is +91 90000 12345.
My customer ID is CUS-104582.
Detection

Possible merged detections:

PERSON
Aarav Mehta

EMAIL
aarav.mehta@example.com

PHONE
+91 90000 12345

CUSTOMER_ID
CUS-104582
Sanitized Request
My name is <<PII_PERSON_001>>.
My email is <<PII_EMAIL_001>>.
My phone number is <<PII_PHONE_001>>.
My customer ID is <<PII_CUSTOMER_ID_001>>.
Request Sent to GPT
My name is <<PII_PERSON_001>>.
My email is <<PII_EMAIL_001>>.
My phone number is <<PII_PHONE_001>>.
My customer ID is <<PII_CUSTOMER_ID_001>>.

The external LLM does not receive the original values.

GPT Response
Hello <<PII_PERSON_001>>.

Your request associated with
<<PII_CUSTOMER_ID_001>> has been received.
Restored Response
Hello Aarav Mehta.

Your request associated with
CUS-104582 has been received.
Security Principle

The central security principle of the project is:

Sensitive information should be detected and sanitized before being sent
to an external LLM.

The middleware should therefore sit directly between the application and the
LLM.

Application
     |
     | Original data
     v
PII Middleware
     |
     | Sanitized data
     v
External LLM

The external LLM should not receive the original PII values when the
middleware is functioning correctly.

Current Implementation

The current repository contains initial experiments for PII detection.

Current files:

pii-middlewareproject/
│
├── .gitignore
├── llama_pii_test.py
└── test_gliner.py
llama_pii_test.py

This file currently tests local Llama-based PII extraction.

It includes:

Model loading
Tokenizer loading
Prompt construction
PII extraction
JSON parsing
Entity validation
Hallucination rejection
Duplicate removal
Result reporting
Generation-time measurement
test_gliner.py

This file is retained from an earlier GLiNER-based experiment.

GLiNER is not part of the current target architecture.

The current direction is:

Presidio + Llama

rather than:

Presidio + GLiNER
Current Llama Test

The current Llama test uses input similar to:

My name is Aarav Mehta.
I was born on 14 March 1992.
My email address is aarav.mehta@example.com.
My phone number is +91 90000 12345.
I live at 42 Palm Grove Road, Panaji, Goa 403001, India.

My customer ID is CUS-104582 and my employee ID is EMP-7821.
I work as a Software Engineer at Blue Horizon Technologies Pvt. Ltd.

My passport number is P0000001.
My driver's license number is DL-XX-000001.

My emergency contact is Priya Mehta.
Her phone number is +91 90000 12346.

The model is instructed to return entities in structured JSON.

The output is then validated against the original input.

Current Llama Limitation

The current experiment demonstrated an important limitation.

The Llama model can identify PII, but on CPU it may:

Produce malformed JSON
Stop before completing the JSON response
Produce incomplete output
Require significant generation time
Occasionally require stronger output constraints

For example, a previous test produced a response that contained multiple
correct entities but ended with incomplete JSON.

The JSON parser consequently rejected the response.

This is why the Llama component should not currently be treated as the only
source of truth.

The middleware architecture therefore keeps Presidio as an important
structured detection component while Llama is evaluated for contextual
detection.

Performance

Initial local testing showed that Llama inference on CPU is significantly
slower than traditional rule-based detection.

A previous local test reported approximately:

Model loading:
~5 seconds

Llama generation:
~44 seconds

These values are environment-dependent and should not be considered final
benchmarks.

Performance will need to be evaluated again once the complete middleware
pipeline is implemented.

The final benchmark should measure:

Presidio detection time
Llama detection time
Detection merge time
Sanitization time
Placeholder generation time
LLM request time
Restoration time
Total middleware latency
Project Structure

The intended project structure will eventually become similar to:

pii-middlewareproject/
│
├── README.md
├── .gitignore
│
├── middleware/
│   ├── detector.py
│   ├── presidio_detector.py
│   ├── llama_detector.py
│   ├── merger.py
│   ├── sanitizer.py
│   ├── placeholders.py
│   ├── restorer.py
│   └── middleware.py
│
├── tests/
│   ├── test_presidio.py
│   ├── test_llama.py
│   ├── test_merger.py
│   ├── test_sanitization.py
│   └── test_end_to_end.py
│
├── examples/
│   └── example_request.py
│
├── requirements.txt
│
└── llama_pii_test.py

The repository is currently at an earlier experimental stage, so the final
structure has not yet been implemented.

Technology Stack

Current technologies being explored:

Technology	Purpose
Python	Main development language
Microsoft Presidio	PII detection
PyTorch	Local model inference
Hugging Face Transformers	Llama model loading and inference
Llama 3.2 1B Instruct	Contextual PII detection experiment
GPT / External LLM	Target downstream application
Git	Version control
GitHub	Source-code repository
Development Environment

The project is currently being developed on Windows.

Python environment:

Python 3.11.x

The project uses separate virtual environments for local experiments.

Virtual environments are intentionally excluded from Git.

For example:

llama_env/
llama311_env/

are not committed to the repository.

Downloaded model files are also excluded from Git.

Installation

Create a Python virtual environment:

python -m venv llama311_env

Activate it:

.\llama311_env\Scripts\Activate.ps1

Install required packages as needed:

pip install torch
pip install transformers

Additional Presidio dependencies will be included as the middleware is
implemented.

Running the Current Llama Test

From the project directory:

.\llama311_env\Scripts\python.exe .\llama_pii_test.py

The program loads:

meta-llama/Llama-3.2-1B-Instruct

and runs the PII extraction test.

The output includes:

Model loading time
Generation time
Raw model response
Validated entities
Total entities
Entity Validation

The current Llama experiment contains a validation layer.

The model output is not blindly trusted.

For example, if the model returns:

{
  "type": "PERSON",
  "value": "Unknown Person"
}

but the value does not exist in the input, it is rejected.

Conceptually:

if value not in original_text:
    reject_entity()

This is intended to reduce the impact of hallucinated entity values.

Detection Confidence

Presidio provides confidence scores for many detections.

The eventual merger should take confidence into account.

For example:

Presidio
PERSON -> Aarav Mehta
Score  -> 0.85

Llama
PERSON -> Aarav Mehta
Score  -> 1.00

The merger can use detector source, confidence, entity type, and span
information to select the final representation.

The exact merger policy has not yet been finalized.

Testing Strategy

The project will eventually test the middleware using several categories of
input.

Standard PII
Name
Email
Phone
Address
Identification Information
Passport
Driver's license
National ID
Customer ID
Employee ID
Account ID
Financial Information
Bank account
IBAN
Card-related identifiers
Network Information
IP address
Contextual PII

Examples where entity meaning depends on context.

Multiple People

Example:

Aarav Mehta contacted Priya Nair.

The system should identify both people independently.

Repeated PII

Example:

Aarav Mehta called Aarav Mehta.

The middleware should maintain consistent placeholder mapping where
appropriate.

False Positive Testing

Detection systems may sometimes classify non-PII values incorrectly.

For example:

Ticket number: TKT-2026-98147

may be incorrectly classified by a generic recognizer as another entity type.

The merger and sanitization policy should therefore distinguish between:

Detection

and:

Final sanitization decision

This is one of the important areas for future development.

False Negative Testing

The system must also be tested against PII that is difficult to detect.

Examples include:

My client number is CUS-482917.

or:

Please contact Aarav at his usual address.

Contextual information may require model-based detection or application-specific
recognizers.

Known Limitations

The current project is still under development.

Known limitations include:

The complete Presidio + Llama merger has not yet been implemented.
Llama structured JSON output is not always reliable.
Local CPU inference can be slow.
Sanitization policy is still being designed.
Placeholder management is not yet implemented as a complete middleware
component.
GPT integration is not yet implemented.
Placeholder restoration is not yet implemented as a complete end-to-end
component.
Final performance benchmarks have not yet been established.
Entity conflict-resolution rules still need to be defined.
Production-level security controls have not yet been implemented.
Security Considerations

This project is intended as a privacy middleware experiment and should not
currently be considered a production-ready security product.

Particular attention should be given to:

Original PII

Original PII should remain inside the controlled middleware context.

Logs

Sensitive values should not be written to logs in production.

Debug logging should avoid printing:

Names
Emails
Phone numbers
Addresses
IDs
Financial information
Placeholder Mapping

Placeholder mappings should be protected because they contain the relationship
between sanitized values and original PII.

External LLM

The middleware must ensure that the request sent to an external LLM contains
only the sanitized representation.

Error Handling

Failures should fail safely.

If sanitization fails, the system should not automatically send the original
PII-containing request to the external LLM.

Development Status

Current status:

+-----------------------------------+-------------+
| Component                         | Status      |
+-----------------------------------+-------------+
| Git repository                    | Completed   |
| GitHub repository                 | Completed   |
| Microsoft Presidio testing        | Completed   |
| Llama environment                 | Completed   |
| Llama model loading               | Completed   |
| Llama PII experiment              | Completed   |
| Llama JSON validation             | Prototype   |
| Detection merger                  | Planned     |
| Sanitization policy               | Planned     |
| Placeholder engine                | Planned     |
| GPT integration                   | Planned     |
| Placeholder restoration           | Planned     |
| End-to-end middleware             | Planned     |
| Performance benchmarking          | Planned     |
+-----------------------------------+-------------+
Current Target Architecture

The architecture we are currently following is:

                         YOUR APPLICATION
                                |
                                v
                       +------------------+
                       |  PII MIDDLEWARE  |
                       +--------+---------+
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
          +-------------+               +-------------+
          |  PRESIDIO   |               |    LLAMA    |
          |             |               |   3.2 1B   |
          | Detection   |               | Detection   |
          +------+------+               +------+------+
                 |                             |
                 +-------------+---------------+
                               |
                               v
                       +---------------+
                       |    MERGER     |
                       +-------+-------+
                               |
                               v
                       +---------------+
                       | SANITIZATION  |
                       |    POLICY     |
                       +-------+-------+
                               |
                               v
                       +---------------+
                       | PLACEHOLDER   |
                       |    ENGINE     |
                       +-------+-------+
                               |
                               v
                         SANITIZED TEXT
                               |
                               v
                              GPT
                               |
                               v
                       SANITIZED RESPONSE
                               |
                               v
                       +---------------+
                       |  RESTORATION  |
                       +-------+-------+
                               |
                               v
                         YOUR APPLICATION
Future Implementation

The next major development phase is to combine the individual experiments
into one middleware.

The planned sequence is:

Phase 1 — Presidio Integration

Create a reusable Presidio detector:

Input
  ↓
Presidio Analyzer
  ↓
Standardized Detection Objects
Phase 2 — Llama Integration

Create a reusable Llama detector:

Input
  ↓
Llama
  ↓
Structured Entity Output
  ↓
Validation
  ↓
Standardized Detection Objects
Phase 3 — Detection Merger

Combine:

Presidio results
+
Llama results

and resolve:

Duplicates
Overlaps
Conflicts
Confidence
Entity types
Phase 4 — Sanitization

Apply the organization's sanitization rules.

Phase 5 — Placeholder Engine

Generate stable placeholders and maintain the mapping.

Phase 6 — LLM Integration

Send only sanitized text to GPT or another external LLM.

Phase 7 — Restoration

Restore placeholders in the LLM response.

Phase 8 — End-to-End Testing

Test the complete flow:

Application
→ Detection
→ Merge
→ Sanitization
→ Placeholder
→ LLM
→ Restoration
→ Application
Future Goals

The long-term goal is to turn the prototype into a reusable PII protection
middleware layer that can be integrated into applications using external LLMs.

Potential future capabilities include:

Configurable PII policies
Application-specific entity recognizers
Configurable confidence thresholds
Multiple LLM providers
REST API middleware
Python SDK
Request/response interception
Structured JSON support
Streaming response support
Audit logging without exposing PII
Performance optimization
Better model-based detection
Robust overlap resolution
Automated testing
Security testing
Production deployment support
Project Philosophy

The project follows a defense-in-depth approach.

No single detector is assumed to be perfect.

Instead:

Presidio
    +
Llama
    +
Validation
    +
Detection Merger
    +
Sanitization Policy
    +
Placeholder Protection

form the protection pipeline.

The important principle is that detection and sanitization are separate
stages.

A detection result is an observation.

The sanitization policy determines what should actually be protected.

Disclaimer

This repository represents an actively developing internship/project
prototype.

The current implementation is intended for experimentation, testing, and
architecture development.

It should not be considered a complete production-grade privacy or security
solution without additional testing, security review, threat modeling,
performance testing, and operational controls.

Author

Krush28

GitHub:

https://github.com/Krush28