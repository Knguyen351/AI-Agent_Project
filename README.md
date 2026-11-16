# Career Launch Agent

A Streamlit search dashboard for IT jobs in North Carolina, South Carolina, and listings explicitly marked US remote. Open the app, select filters, and follow links to the original employer postings. The dashboard opens directly to search without an account or signup configuration.

## Deploy to Streamlit Community Cloud

1. Extract the ZIP, then commit the project files to the GitHub branch used by your Streamlit app. Keep `app.py`, `requirements.txt`, and the supporting Python and JSON files together.
2. For an existing deployment, update the files in the same location the app already uses. For a new deployment, select your repo and branch and set the main file path to `app.py` if the files are at the repo root, or `career_launch_agent/app.py` if you kept the folder.
3. Open the hosted app. It should show **Find IT jobs**. Job search requires no Streamlit Secrets. You can remove the old `CAREER_SIGNUP_EMAILS` entry if it is still present.

## Run on Windows

With Python 3.12 installed, extract the ZIP and double-click **Start_Career_Launch_Agent.cmd**. The launcher installs dependencies as needed and opens the local dashboard. Keep the launcher window open while using it.

For a terminal-based setup, install `requirements.txt` and run `python -m streamlit run app.py` from the project folder.

## Search filters

- **States** — Select NC, SC, or both. State selection filters site-based results.
- **IT roles** — Choose help desk and desktop support, networking, data center, systems and cloud, or cybersecurity.
- **Work location** — Search site-based jobs, include listings explicitly labeled US remote, or search only those remote listings. Site-based results may include hybrid roles. Check the posting for the actual schedule and remote eligibility.
- **Employers** — Select specific configured employers or leave the field blank to search all of them.
- **Keyword or city** — Enter a phrase such as `Windows`, `Charlotte`, or `CompTIA A+` to narrow results by title, employer, location, or description.

Click **Find IT jobs** to search live employer boards. Results can be cached for up to 15 minutes. Coverage depends on the sources in `sources.json`. Some adapters focus on the Carolinas and specific role families, so remote and specialty searches can return few or no results. The dashboard searches advertised titles and job descriptions. Review the employer page for current status and qualifications.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit filters and job results |
| `sources.json` | Configured employer boards |
| `job_sources.py` | Employer feeds and shared job matching logic |
| `career.py` | Shared job search and optional digest logic |
| `manage.py` and `database.py` | Existing private pilot tooling |

The public dashboard does not access saved profiles, application history, or email settings. Existing pilot data remains in its database if you have one. The optional digest tools still require a separately configured worker and SMTP credentials. Search does not start that worker or send email.
