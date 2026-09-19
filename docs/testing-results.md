# Testing Results

## Overview

Testing was completed across the validation, controller, storage and GUI modules, together with manual GUI checks and a small performance test. Automated tests were designed to isolate individual modules where appropriate, while manual testing was used to confirm end-to-end behaviour from a user perspective.

## Automated Test Summary

| Area | Tests Run | Passed | Failed / Error | Summary |
|---|---:|---:|---:|---|
| Validation | 16 | 16 | 0 | Validation rules behaved as expected for the scenarios tested. |
| Controller | 20 | 17 | 3 | Update operations did not apply the same validation rules as Create. |
| Storage | 19 | 19 | 0 | JSON loading, persistence, CRUD operations, ID handling and search behaved as expected. |
| GUI | 6 | 5 | 1 | Validation errors raised by the controller were not displayed by the GUI. |
| Performance | 4 | 4 | 0 | All measured operations completed well below the one-second target using 500 records. |

## Key Findings

### T01 - Update does not apply validation

Validation is applied when records are created, but the same rules are not consistently applied when records are updated.

Example:
- Creating a Client with telephone number `12345` is correctly rejected as invalid.
- If a valid Client is created first and the telephone number is later changed to `12345`, the Update is accepted.

The same issue was reproduced with:
- a blank Airline name;
- a past Flight date.

This indicates that Update currently bypasses validation before data reaches storage.

### T02 - Validation errors are not displayed by the GUI

The validation layer can correctly reject invalid data, but the GUI does not currently display the validation error to the user.

Example:
- Creating a Client with telephone number `12345` is rejected by validation.
- No useful error message is shown in the GUI explaining why the record was not created.

The GUI currently handles `ValueError`, while the validation layer raises `ValidationError`.

### T03 - Validation usability and input guidance

Manual testing identified a usability issue with required fields and accepted input formats.

Example:
- A telephone number entered as `07123 456789` was rejected because it contained a space.
- The same number without spaces was accepted.
- The GUI does not currently indicate which fields are mandatory or explain accepted input formats.

This makes it difficult for users to understand why otherwise reasonable-looking input has been rejected.

## Manual GUI Testing

The following were tested manually through the running application:

| Test | Result |
|---|---|
| Create Client with valid data | Pass |
| Create Airline | Pass |
| Create future Flight | Pass |
| Create past Flight | Rejected as expected, but no error message shown |
| Update existing record | Pass |
| Delete record | Pass |
| Search | Pass |
| Show All | Pass |
| Persistence after close and reopen | Pass |
| Status bar counts | Pass |
| Client/Airline availability in Flight dropdowns | Pass |

## Performance Testing

Performance was tested using 500 Client records and temporary JSON files. Measurements used `time.perf_counter()` and covered controller-to-storage processing rather than GUI rendering time.

| Operation | Result |
|---|---:|
| Create | 15.582 ms |
| Search | 2.906 ms |
| Update | 9.693 ms |
| Delete | 9.916 ms |

All measured operations completed below the one-second target.

## Next Step

After the identified defects are corrected, the existing failed tests should be rerun as regression tests to confirm that the fixes work without affecting previously passing behaviour.