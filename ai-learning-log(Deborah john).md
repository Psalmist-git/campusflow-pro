# AI Learning Log — Deborah John

> Project: CampusFlow ticket system  
> Purpose: Record meaningful AI-assisted learning interactions, including independent tests and decisions.  
> Note: This log uses only work and results recorded in my learning conversation. Where a commit SHA or PR link was not provided, it is marked as not recorded rather than invented.

## Interaction #1 — Python dictionary access and `KeyError`

**Problem:** I needed to retrieve ticket details from a Python dictionary.

**My initial understanding:** I tried to access several dictionary keys together using `ticket["id","title","category"]`, expecting Python to return all three values.

**Prompt to AI:** I asked for help understanding the error I got while working with my CampusFlow ticket.

**Useful AI guidance:** A dictionary lookup uses one key at a time. Writing several strings separated by commas inside the brackets creates a tuple key, which is different from the individual keys `"id"`, `"title"`, and `"category"`.

**My independent experiment/test:** I ran my code with the combined-key expression, then changed the code to access and print each field separately.

**Verification source or result:** The first attempt produced `KeyError: ('id', 'title', 'category')`. After changing to individual lookups, the terminal printed the ticket ID, title, category, and affected-user count, including `T001`, `Campus Wi-Fi is down`, `Network`, and `15`.

**Decision:** **Accepted.** The error and the successful output supported the explanation.

**Related file/commit:** CampusFlow ticket code; exact file path and commit SHA were not recorded in this interaction.

**What I can now explain without AI:** A dictionary stores values under keys. To retrieve one value, I use its key, such as `ticket["id"]`. Putting comma-separated keys inside one pair of brackets does not retrieve several values automatically.

---

## Interaction #2 — Debugging the priority rule and a type error

**Problem:** I was implementing CampusFlow's ticket-priority logic using urgency and the number of affected users.

**My initial understanding:** I wrote a condition similar to `if "urgency high" and "affected_users" >= 10:`. I thought these quoted phrases would check the ticket's urgency and affected-user count.

**Prompt to AI:** I shared the condition and asked for help after Python raised a comparison error.

**Useful AI guidance:** Quoted text is a string literal. To check a ticket, I need to read the values from the ticket data and compare the numeric affected-user value with an integer. A condition should check the actual urgency value and the actual affected-user count, rather than compare the text `"affected_users"` to `10`.

**My independent experiment/test:** I ran the condition and then tried comparing the quoted string `"affected_users"` directly with `10`.

**Verification source or result:** The terminal raised `TypeError: '>=' not supported between instances of 'str' and 'int'`. This confirmed that the expression was comparing a string with an integer. I have not recorded a successful final test of the corrected priority condition in this log.

**Decision:** **Improved, pending full verification.** The error showed why the original comparison was invalid. The corrected rule still needs to be tested with representative ticket values before I can claim the priority engine is fully verified.

**Related file/commit:** CampusFlow priority-engine work; exact file path and commit SHA were not recorded here.

**What I can now explain without AI:** Text inside quotes is treated as a string. If I want to compare the number of affected users with `10`, I must access the ticket's actual numeric value, for example through the relevant dictionary key, and ensure the value is an integer.

---

## Interaction #3 — Running automated tests for ticket storage

**Problem:** I needed to check whether the CampusFlow storage code behaved correctly for empty files and invalid or malformed JSON.

**My initial understanding:** I knew I should run automated tests, but I needed to check the test-discovery command and read the results to see which cases passed.

**Prompt to AI:** I worked through checking the project test folder and running the Python `unittest` suite.

**Useful AI guidance:** Use Python's test discovery to run the test files, and inspect the individual test names and statuses instead of assuming that code works because it runs.

**My independent experiment/test:** I listed the test folder and ran:

```bash
python3 -m unittest discover -s test -v
```

**Verification source or result:** The recorded terminal output showed these storage tests passing:
- `test_empty_file_returns_empty_list` — `ok`
- `test_invalid_json_is_rejected` — `ok`
- `test_malformed_json_is_not...` — the captured output was truncated, so I am not recording its final status here.

The test folder contained `test_storage.py`, `test_tickets.py`, and `test_workflow.py`. I am not claiming that every test passed because the complete final output is not available in this record.

**Decision:** **Accepted with a limitation.** The visible output verifies that the empty-file and invalid-JSON storage tests passed. I would need the complete test output to report the status of every test accurately.

**Related file/commit:** `test/test_storage.py`; test command: `python3 -m unittest discover -s test -v`. Commit SHA or PR link: not recorded.

**What I can now explain without AI:** Automated tests check expected behavior. I can run the test suite from the project directory and read each result. I should report only the outcomes I actually observed, not assume that unseen tests passed.

---

## Reflection

These interactions helped me practise reading Python errors, understanding dictionary access, checking types in conditions, and using automated tests as evidence. AI guidance helped me investigate the problems, but I used terminal output to verify the results that are marked as verified above.

**Evidence still to add:** Record the final successful priority-rule tests, the complete test-suite result, and relevant commit SHAs or pull-request links when those checks are actually completed.
