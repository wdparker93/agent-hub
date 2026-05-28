# Will Parker — Detailed Professional Context

This document is the authoritative source of truth for answering questions about Will Parker's
background, experience, skills, and projects. It is intentionally more detailed than a resume.

---

## Professional Summary

Will Parker is a software engineer at Motion Industries in Atlanta, GA, focused on the Prophet 21
ERP platform using C# and SQL. He works on cross-system integrations with PeopleSoft, Microsoft
D365, and Google Cloud, and has recently emphasized AI tooling — building multi-agent systems and
RAG knowledge base agents. Before transitioning into software, he spent four years as an R&D
semiconductor process engineer at CreeLED Inc.

<!-- Expand with anything else that captures your overall trajectory or what kind of work you do best -->

---

## Work Experience

### Software Engineer II — Motion Industries (Prophet 21 Team)
**Dates:** December 2024 – Present
**Location:** Birmingham, AL (Atlanta, GA)

<!-- Describe day-to-day ownership, team structure, biggest wins since promotion, current projects -->

### Software Engineer I — Motion Industries (Prophet 21 Team)
**Dates:** December 2023 – December 2024
**Location:** Birmingham, AL

#### Multi-agent AI systems for engineer onboarding and workflow automation
- Authored Confluence knowledge base articles and trained agents on codebase, Confluence articles, Prophet 21 documentation, Prophet 21 API definitions, and Prophet 21 database schema to guide new engineers through examples and explain how to author new software in accordance with team's architectural patterns.
- One agent represented an application developer and was trained on the codebase, Confluence articles, Prophet 21 documentation, Prophet 21 API definitions, and Prophet 21 database schema. The agent was coached to develop under our home-grown framework we developed to overcome inherent Prophet 21 system limitations and allow us to further and more reliably extend its functionality via C# extensions (what Prophet 21 terms business rules)
- Another agent represented limitations of the application and was trained on Prophet 21 documentation, Prophet 21 API definitions, Prophet 21 database schema, and a known list of limitations that Prophet 21 has that limit the ability of the developer agent to execute a request. Some limitations are clearly described by the application's documentation, but many were discovered by our team and are undocumented, requiring seat time to triage, troubleshoot, and affirm a newly discovered limitation.
- Another agent was trained on the entirety of the repo, all documentation, API definitions, database schema, and Prophet 21 help pages and serves as a knowledge base agent. Its knowledge is sufficient to route queries to the appropriate specialist agent.
- Each agent has its own set of skills.
- The developer agent can conduct feasibility analyses and validate via friction against the application agent.
- Feasibility analyses reference ADO and look for unpointed stories in the backlog. Prior to weekly backlog refinement, the developer agent will execute feasibility analyses and, if firmly feasible, author the code required to complete the request along with unit tests after posting a comment to the ADO story summarizing its analysis. All the agent requires is the information on the ADO ticket itself - no extra guidance required as it is trained to translate plain text requests to code based on documentation and Prophet 21 schemas and API definitions.
- The developer agent can also author code and unit test upon request from the developer and answer queries.

#### RAG knowledge base orchestrator (Confluence / Prophet 21 docs)
- This knowledge base agent also serves as the orchestrator in the multi-agent system described above, routing queries to the appropriate specialist agent (developer agent or application limitations agent).
- Trained on the entirety of the Prophet 21 application's help pages, our own internal Confluence pages, our codebase containing custom business rules and integration applications, the Prophet 21 database schema, and the Prophet 21 API definitions which roughly translate to what a user sees on a screen.
- The database schema and API definitions change as we add user-defined fields and tables that extend the functionality of Prophet 21. Additionally, Confluence documentation changes as we add or update pages.
- I authored an ADO pipeline that automatically retrieves the updated database schema, API definitions, and Confluence pages once per week, indexes and tags them into its knowledge base, and creates a PR into main with me and the product owner listed as approvers.
- A lightweight tagging framework was used to make the knowledge base agent faster and to appropriately categorize information. In the absence of a tagging framework, the agent hallucinated connections between knowledge base data points that were often incorrect and ran slower.
- Entry points were also created so the knowledge base agent can evaluate a request and proceed down a decision tree, enabling better and faster RAG.

#### Automated deployment and release cadence via Azure DevOps pipelines
- I was the first software engineer at Motion who had spent time developing applications in Prophet 21. Prior to my start, external companies had authored a handful of business rules that resided on a few different peoples' laptops. There was a git repository, but there was no version control.
- I version controlled all the rules I could find and built the entire repo from the ground up.
- Since our team was small with only me working on it for the first year, we did not have a release train framework established. Coordination was simple with only one person.
- Over the past year, we've onboarded three new developers who contribute to the repository and now have a total of four developers and one architect who regularly author code changes. The need for coordination became apparent as production releases became harder to plan.
- I created a release train process and proposed it to management and the development team to ensure everyone could agree on a framework that would make releases scheduled and predictable.
- I ensured the release train process would not create work for my team by automating a weekly email that gets sent to the development team that contains instructions for how to get work completed and requirements for what is allowed to go into production. This required a C# business rule in Prophet 21 as well as the creation of a user-defined table that housed moratorium dates so as to specify in the release email that no release would happen if the upcoming release date fell on a moratorium date.
- The automated release train process standardized the team's approach to reduce cognitive overhead for management and senior engineers while still allowing us to be flexible and deploy quickly should we need to make an urgent update.
- Also authored a separate ADO pipeline (part of the RAG knowledge base orchestrator work) that automatically retrieves and re-indexes updated Prophet 21 schema, API definitions, and Confluence pages weekly, keeping the agent's knowledge base current without manual intervention.

#### EDI integrations (PowerShell / .NET)
- As part of the migration of a legacy system onto Prophet 21, we had to ensure Prophet 21 could conduct business through EDI (Electronic Data Interchange).
- Prophet 21 has hooks that can be leveraged to generate EDI, but itself did not produce a viable EDI document. It either generated a tab-delimited flat file in response to an outbound EDI transaction or imported a tab-delimited flat file that corresponded to an inbound transaction.
- Motion has its own EDI that authors maps - i.e. documents that translate from EDI to another file format and vice versa.
- This project required developing the understanding of the flat files that Prophet 21 outputs by default, determining what additional data points, if any, are needed to ensure the flat files contain enough data to produce a valid EDI document, communicating mapping requirements to the mapping team, and authoring an ETL pipeline that takes raw data, enhances it with additional data points, and load it into Prophet 21 or the mapping team's application.
- This application was built using a C# console application that runs every 5 minutes. This application takes unenhanced flat files, parses them, executes database lookups to ensure they are either ready for import into Prophet 21 in accordance with its specifications or enhanced to include additional fields the EDI mapping team needs to fully produce a viable outbound transaction.
- A suite of PowerShell scripts that resides on a jump server facilitated the transfer of files between the EDI mapping team's application and my C# application. These PowerShell scripts also run every 5 minutes via a Windows scheduled task.
- In total, the EDI application ingested $810,000 of inbound sales orders from customers in the first year. It also processes $1M of rebates per month.
- The current set of EDI transactions include inbound 850 (sales order from a customer), inbound 810 (vendor invoice), inbound 855 (purchase order acknowledgements from vendors), inbound 856 (advance ship notifications from vendors), inbound 849 (vendor responses to rebate requests), outbound 850 (outbound purchase orders to vendors), outbound 810 (invoices to customers), outbound 856 (outbound advance ship notifications to customers), outbound 844 (request for rebates to vendors)

#### PeopleSoft integrations via Prophet 21 APIs

#### Reusable .NET Framework libraries

#### Backend and full-stack ERP enhancements (80%+ test coverage)

#### Event-based C# enhancements publishing to Google Cloud Pub/Sub

#### Technical contact for cross-team integration projects

---

### Associate Software Developer — Motion Industries (eBusiness Team)
**Dates:** February 2023 – December 2023
**Location:** Birmingham, AL

<!-- Describe what the eBusiness team owned, your responsibilities, key deliverables -->

### Software Developer Trainee — Motion Industries (eBusiness Team)
**Dates:** February 2022 – February 2023
**Location:** Birmingham, AL

#### EDI processing pipeline updates (Java)

#### Reporting automation (Python, Java, SQL)

#### Java backend refactoring

#### OCR application for invoice and order PDF ingestion

#### Visual Basic to C# security remediation

---

### R&D Semiconductor Process Engineer II — CreeLED Inc.
**Dates:** (promotion date) – January 2022
**Location:** Durham, NC

#### Optimize and improve semiconductor manufacturing processes

#### Automated data extraction and reporting processes

### R&D Semiconductor Process Engineer I — CreeLED Inc.
**Dates:** July 2017 – (promotion date)
**Location:** Durham, NC

Started career here after graduating with a Chemical Engineering degree from the University of Alabama. Gained first exposure to computer programming through automating data workflows in a semiconductor R&D environment.

#### Optimize and improve semiconductor manufacturing processes

#### Automated data extraction and reporting processes

---

## Skills

### Languages
- C# (primary, production, Prophet 21 / .NET Framework / .NET)
- SQL (production, ERP queries and reporting)
- Python (automation, AI tooling, scripting)
- Java (EDI processing, reporting, backend)
- PowerShell (EDI integrations, DevOps scripting)
- JavaScript / React (portfolio site, side projects)
- HTML / CSS

### Frameworks & Libraries
- .NET Framework / .NET (C# backend, reusable libraries)
- React (portfolio page, Lobbyist Donation Tracker)

<!-- Add any specific NuGet packages, ORMs, or testing frameworks worth mentioning -->

### Cloud & Infrastructure
- Azure DevOps (CI/CD pipelines, release automation)
- Google Cloud Platform — Pub/Sub, Associate Cloud Engineer certified
- <!-- Add any other GCP services: Cloud Run, GCS, BigQuery, etc. -->

### Databases
- SQL Server (primary, Prophet 21 ERP)
- MySQL (Lobbyist Donation Tracker side project)

<!-- Add any others used in production or side projects -->

### Tools & Practices
- Azure DevOps (pipelines, boards, repos)
- EDI / cXML integration
- APIs (REST, Prophet 21 APIs)
- AI-assisted development (multi-agent systems, RAG, Anthropic Claude)
- Test-driven development (80%+ coverage on ERP work)
- Agile / sprint-based delivery

---

## Projects

### GrooveVision (Spotify YouTube Connector)
**Repo:** https://github.com/wdparker93/spotify-youtube-connector
**Stack:** Chrome Extension (JavaScript), Windows Companion App (C# / .NET)

A Chrome extension that automatically finds and opens the YouTube music video for whatever is
currently playing in Spotify. Includes a native Windows companion app that the extension
communicates with.

<!-- Add detail: how the extension detects the current song, how the companion app works, what
     APIs are used, any interesting technical challenges -->

---

### Improv Helper
**Repo:** https://github.com/wdparker93/improvisation-helper
**Stack:** C# / Windows

A Windows application that listens to and captures MIDI keyboard input to assist with
improvisation practice.

<!-- Add detail: what problem it solves for you, how the MIDI capture works, what features it has -->

---

### Portfolio Page
**Repo:** https://github.com/wdparker93/portfolio-page
**Stack:** React, JavaScript

Personal portfolio site showcasing projects and professional background.

---

### Lobbyist Donation Tracker
**Repo:** https://github.com/wdparker93/lobbyist-donation-tracker
**Stack:** React, MySQL, Lobbying Disclosure Act API

A web app that queries the Lobbying Disclosure Act API to track and visualize lobbyist donations.

<!-- Add detail: what motivated the project, what queries/visualizations it supports -->

---

### Connect4
**Stack:** Java

A Java implementation of the Connect4 game.

<!-- Add detail: was this command-line, GUI, multiplayer? Any notable design decisions? -->

---

### Bumper Cars
**Stack:** C (multi-threaded)

A multi-threaded C program simulating bumper cars.

<!-- Add detail: what concurrency model, what the simulation does, academic or personal? -->

---

## Education

### Computer Programming Certificate — North Carolina State University
**Graduated:** August 2021
**Relevant coursework / notes:** <!-- Add courses or highlight of the program -->

### Bachelor of Science in Chemical Engineering — University of Alabama
**Graduated:** May 2017
**Relevant coursework / notes:** <!-- Add anything relevant, e.g. data analysis, programming courses -->

---

## Other

### Certifications
- Google Cloud Certified Associate Cloud Engineer (October 2024 – October 2027)

### Interests & Activities
<!-- Anything relevant to who you are professionally or personally, e.g. music/MIDI given Improv Helper -->
