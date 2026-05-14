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

## Misc Discussion Notes

### Choice of technologies

> Feel free to use any libraries or packages you feel are necessary to complete this task, but be ready to justify your choices.

This was a discussion with an LLM, usually I blindly reach for pandas, however that may not be the best choice.
I've put the projects brief into gemini in order to have a conversation with the 

Here is the summary of our architectural deep dive, with the requested character replacements applied:

#### Summary of ETL Architecture Discussion

The conversation focused on building a scalable, "mini-production" ETL framework using dbt, Postgres, and Python, specifically handling local CSV ingestion with an eye toward future cloud migration.

##### Key Highlights:

The Role of DuckDB: We identified DuckDB as an ideal "bridge" for the analytical stack. Its columnar nature and ability to query CSVs directly make it significantly faster than row-based Postgres for initial ingestion it also can has great dbt support meaning that data-engineers with bad python skills can still maintain the etl layer

- Architecture Pattern: To ensure the system is scalable, we implemented a Strategy Pattern on the file watchers. This decouples how a file is detected from how it is processed.

###### Component Breakdown:

- Processor (`BetIngestor`): Contains the core logic using DuckDB to "attach" to Postgres and move data. It is agnostic of where the file originates.
- Trigger Interface (`BaseTrigger`): An abstract base class defining the contract for file detection.
- Local Implementation (`WatchdogTrigger`): Uses the `watchdog` library for event-driven file monitoring on a local mount.
- Cloud Path: The design allows for an `S3EventTrigger` to be swapped in later without modifying the data processing logic.

###### Engineering Best Practices:

- Idempotency: Moving files to a `processed/` directory to prevent duplicate processing.
- Event-Driven: Using OS-level events (`on_closed`) rather than polling to save resources.
- Decoupling: Using Dependency Injection to swap triggers based on environment variables (`APP_ENV`).

##### Proposed Tech Stack:

- Ingestion/Processing Interface: Python_Foundations + DuckDB
- Monitoring Interface: Adhoc file watcher, however built so that:  Watchdog (Local), SQS (Cloud) or alternatives could work in its place
- Warehouse: Postgres 11 (via Docker)
- Transformation: dbt (as the next logical layer)

> [!NOTE]
> I think that I've over engineered this, I've tried to walk a fine line of building a solid extensible python base and wasting time not on implementation but I feel like this balance is out of whack. If I had all the time in the world I'd add a source and destination logic (i've added a todo for referecne)



---
[pep621Link]: https://peps.python.org/pep-0621/
[minimalFileWatcherLink]: https://medium.com/@efpa97_ltep_technologies/an-easy-filewatcher-for-python-no-side-effects-quick-setup-watchdog-alternative-c10e49c03071
