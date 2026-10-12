## Fellow: Deborah John

### Interaction #1 — Python Dictionaries and KeyError

**Problem:**
I needed to understand how to retrieve multiple fields from a ticket dictionary in my CampusFlow project.

**My initial understanding:**
I thought I could retrieve several dictionary values by putting multiple keys inside one pair of square brackets.

**Prompt to AI:**
I was working with a ticket dictionary and tried to access its `id`, `title`, and `category` fields together. I needed help understanding why my code produced an error.

**Useful AI guidance:**
AI explained that a dictionary lookup using square brackets expects one key at a time. When I wrote `ticket["id","title","category"]`, Python interpreted the comma-separated values as a tuple key rather than three separate dictionary keys.

I learned that I could retrieve the fields individually:

- `ticket["id"]`
- `ticket["title"]`
- `ticket["category"]`

**My independent experiment/test:**
I ran my Python file from the terminal:

`/usr/bin/python3 /home/student/CampusFlow/campusflow/tickets.py`

My initial attempt produced:

`KeyError: ('id', 'title', 'category')`

I then used separate dictionary lookups to retrieve the required fields.

**Verification source or result:**
The terminal displayed the ticket information:

- `T001`
- `Campus Wi-Fi is down`
- `Network`

**Decision:**
Accepted and improved. The error message showed that Python was treating my comma-separated keys as one tuple key. I corrected my approach by accessing each dictionary field separately and observed the expected output.

**Related file/commit:**
`campusflow/tickets.py`

**What I can now explain without AI:**
A dictionary stores information as key-value pairs. Square brackets allow me to retrieve a value using its key. If I want three different values, I must access their keys separately unless I have deliberately created a tuple key in the dictionary.

---

### Interaction #2 — Automated Testing and Test Discovery

**Problem:**
I needed to run the CampusFlow automated tests and make sure Python could discover the test files and import the project modules.

**My initial understanding:**
I knew I needed automated tests, but I had difficulty getting the test files and imports working correctly. I learned that having test code written does not automatically mean Python will discover and execute it.

**Prompt to AI:**
I shared the errors I encountered while trying to run my CampusFlow tests and asked for help understanding the test discovery and import problems.

**Useful AI guidance:**
AI helped me investigate the test directory, Python imports, and test filenames. I learned that test discovery depends on the command I use and the location and naming of the test files.

**My independent experiment/test:**
During debugging, I encountered a `ModuleNotFoundError` and a test filename that was incorrectly written as `test _storage.py`.

I checked my project structure and corrected the filename to `test_storage.py`.

I then ran the tests from the project root:

`python3 -m unittest discover -s tests -v`

**Verification source or result:**
My subsequent test run reported:

- 33 tests run.
- 33 tests passed.
- 0 failures.
- 0 errors.
- Final result: `OK`.

**Decision:**
Accepted and improved. I used the terminal output to check whether the correction worked instead of assuming the tests were successful. The successful test run provided evidence that the tests discovered in that run passed.

**Related file/commit:**
- `campusflow/tickets.py`
- `campusflow/workflow.py`
- `campusflow/storage.py`
- `tests/test_tickets.py`
- `tests/test_workflow.py`
- `tests/test_storage.py`

Note: The test command I actually ran used `-s tests`. My earlier project structure also included a `test` directory, so I learned to check the real directory name before running test discovery.

**What I can now explain without AI:**
Automated tests help me check whether my code behaves as expected. Python's `unittest` framework can discover and execute tests, but I must use the correct directory and ensure the test files and imports are set up properly. A successful test run gives me evidence about the code covered by those tests, rather than proving that every possible situation works.

---

### Interaction #3 — Ticket Priority Rules and Data Types

**Problem:**
I needed to implement priority rules for CampusFlow tickets using their urgency and number of affected users.

**My initial understanding:**
I understood that a ticket's urgency and the number of affected users should influence its priority. However, I confused the names of dictionary fields with the actual values stored in those fields.

**Prompt to AI:**
I shared my priority condition and the Python error I received while comparing `affected_users` with a number.

**Useful AI guidance:**
AI helped me understand that a dictionary key is used to retrieve a value. Writing `"affected_users"` directly refers to a string, not the numeric value stored in the ticket dictionary.

For example, if `ticket` is a dictionary, `ticket["affected_users"]` retrieves the value associated with that key.

I also learned that a numeric comparison such as `>= 10` requires a compatible numeric value.

**My independent experiment/test:**
I tried the following condition:

`if "urgency high" and "affected_users" >= 10:`

Python returned a `TypeError` because the code attempted to compare a string with an integer.

I then tried comparing the string `"affected_users"` directly with `10`, but that produced the same type of error.

**Verification source or result:**
The terminal reported:

`TypeError: '>=' not supported between instances of 'str' and 'int'`

This confirmed that the comparison was being performed between incompatible types.

I have verified the error and its cause. I am not claiming that this particular experiment verified the complete priority engine or all priority rules.

**Decision:**
The original condition needed improvement. I learned to distinguish between a field name written as a string and the value retrieved from a dictionary. The error helped me identify the incorrect comparison.

**Related file/commit:**
`campusflow/tickets.py`

Related ticket example:
- ID: `T001`
- Title: `Campus Wi-Fi is down`
- Category: `Network`
- Urgency: `high`
- Affected users: `15`
- Expected priority: `critical`

The expected priority describes the example ticket; it is not evidence that this particular experiment successfully tested the entire priority engine.

**What I can now explain without AI:**
A dictionary key identifies where a value is stored. Writing `"affected_users"` gives me a string, while `ticket["affected_users"]` retrieves the value from the dictionary. If the value is an integer, I can compare it with another integer. I must also write the urgency condition correctly and test the priority rules with different inputs.