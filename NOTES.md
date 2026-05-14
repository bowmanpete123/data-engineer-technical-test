# Submission Notes

Feel free to add anything you would like to this document to help explain your submission. Things like presumptions that you made, other features and best practices that you would implement in a production grade system etc. Some suggested headings are below.

## Presumptions Made

1. I'm assuming that though the company is handling a low amount of data, we are building this production system to begin scaling, this means
    - I'm going to build this under the guise that it not be over-engineered for the sake of scale that may not materialise (i.e. if the business doesn't grow it won't take years just to add a row to a table properly)
    - That the design though lean must be able to scale if the scale materialises.

## Additional Production Grade Considerations

1. In our first interview Todd said that "Data Engineering is SWE ugly cousin" I feel strongly that there is a disrespect for newer tooling in python, therefore I'm going to look at upgrading the dockerfile to the later tooling for the following reasons:
    - If this will go into production the python version the docker is originally pinned to get to end of life on [October of 2026][EOLpythonLink], if we upgrade ton 3.14 we can go two years without having to worry about EoL python versions (3.14 was chosen as it is still under active maintenance, or bug-fixing as the core team calls it).
    - `requirements.txt` files are TERRIBLE for production, great for prototyping, but dependency management is hell. Most modern python projects work to [PEP621][pep621Link] and create `lock` files similar to package.json. 
    - python does NOT have compile time bugs, this makes it forgiving but you have to deal with everything at run time. The stricter the packaging tooling is the more peace of mind you have about the runtime.


---
[pep621Link]: https://peps.python.org/pep-0621/
