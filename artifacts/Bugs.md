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