### ~~Bugs~~ Features
Jeff Dean once implemented a K-Means classifier incorrectly, and yet his implementation performed better than the original. We, the Black Panthas, live by this mantra.
* When the mobile application retrieves the code, it appends `[data]=` at the beginning.
* In the context parser, certain characters allow the parser to get stuck in a loop. For example, many periods can be appended in a row.
* The accuracy of the algorithm for extracting characters from the image varies widely based on lighting. In some conditions the accuracy is near 100%, and in others it's dismal.
* New lines in code aren't shown in the mobile application.
* The code executor returns a comma-separated list of outputs (instead of newline-separated).
* Some features of Javascript aren't supported, in an effort to improve accuracy. For example, classes aren't supported.
* Occasionally the line sorting algorithm duplicates characters.
* The character processor centers the character in the image, making some characters, like the comma and apostrophe, nearly impossible to distinguish. As a result, the software doesn't support underscores, but this isn't much of an issue anywhere else.

### Product Backlog
## Code reader
* [**Complete**] Algorithm to isolate tokens (6 hours)
	* We want to divide the code into tokens (for example, variable names and function names), for future     	processing.
* [**Complete**] Correct small errors in tokens (12 hours)
	* For example, if one token differs by one character from another, change one so it matches the other.
* [**Complete**] Correct code reader errors (24 hours)
	* Correct other errors, like parentheses instead of brackets

## Execution
* Run the JavaScript
	* [**Complete**] Check against infinite loops (2 hours)
		* Specify a timeout on code execution, so the user can't freeze the server.
	* [**Complete**] Run in separate scope so the user can't overwrite needed functions/variables (3 hours)
		* With native `eval` execution, the user can overwrite necessary functions or variables with their own code. Therefore, we need to isolate their code from the actual server.
* Replace directory after code execution? (8 hours)
	* There might be some way the user could install spyware or modify the directory in which the code is executing. An easy way to fix this (as a safeguard) would be to replace the server directory after the code is finished executing.
* Ensure server can only access certain directories (3 hours)
	* We just need to run the code in a chroot jail.
* Router
	* [**Complete**] Route requests to available VMs (10 hours)
		* Requests come into our cluster to the router VM, which needs to find an available worker VM and send the code to it.
	* [**Complete**] Restart VMs if they aren't responding (10 hours)
		* If a VM is down, we need to reset it to the initial image and restart it.
	* Reset all VMs daily? (1 hour)
		* This will help with any really sneaky hackers. It should be doable by scheduling a `cron` job to run each day at midnight or something.

## Mobile App
* [**Complete**] Camera integration - allow users to take pictures
* [**Complete**] Allow the user to upload a file
* See and answer programming practice questions
* Allowed to enter custom test cases
* Allow users to see all test cases, if they want to look at them
* After parsing code
	* [**Complete**] Show text on screen, allow user to correct any errors
	* Highlight parts of code that we're uncertain about and allow user to correct those more easily
* Question database
	* Provide parameters to code (like if the algorithm requires an array or something)
	* Provided test cases


