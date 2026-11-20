"""US location and career-level classification."""
import re

STATES = dict(pair.split(':') for pair in (
    'AL:Alabama|AK:Alaska|AZ:Arizona|AR:Arkansas|CA:California|CO:Colorado|CT:Connecticut|'
    'DE:Delaware|DC:District of Columbia|FL:Florida|GA:Georgia|HI:Hawaii|ID:Idaho|IL:Illinois|'
    'IN:Indiana|IA:Iowa|KS:Kansas|KY:Kentucky|LA:Louisiana|ME:Maine|MD:Maryland|MA:Massachusetts|'
    'MI:Michigan|MN:Minnesota|MS:Mississippi|MO:Missouri|MT:Montana|NE:Nebraska|NV:Nevada|'
    'NH:New Hampshire|NJ:New Jersey|NM:New Mexico|NY:New York|NC:North Carolina|ND:North Dakota|'
    'OH:Ohio|OK:Oklahoma|OR:Oregon|PA:Pennsylvania|RI:Rhode Island|SC:South Carolina|SD:South Dakota|'
    'TN:Tennessee|TX:Texas|UT:Utah|VT:Vermont|VA:Virginia|WA:Washington|WV:West Virginia|'
    'WI:Wisconsin|WY:Wyoming|PR:Puerto Rico|GU:Guam|VI:US Virgin Islands'
).split('|'))
LEVELS = ['Intern', 'Early', 'Mid', 'Senior']

def career_level(job):
    title = job['title']
    metadata = job.get('experience_level', '')
    evidence = metadata + ' ' + title
    if re.search(r"\b(intern(ship)?|co-?op|apprentice)\b", evidence, re.I):
        return 'Intern'
    if re.search(r"\b(senior|sr[.]?|lead|principal|staff|manager|director|head|iii|iv)\b", title, re.I):
        return 'Senior'
    if re.search(r"senior|director|executive", metadata, re.I):
        return 'Senior'
    if re.search(r"\b(entry|junior|jr|graduate|early|associate|level 1|tier 1|i)\b", evidence, re.I):
        return 'Early'
    if re.search(r"\b(mid|intermediate|ii|level 2|tier 2)\b", evidence, re.I):
        return 'Mid'
    years = re.search(r"\b(\d{1,2})\s*(?:\+|or more)?\s+years?\s+(?:of\s+)?experience",
                      job.get('minimum_qualifications', ''), re.I)
    if years:
        count = int(years.group(1))
        return 'Early' if count <= 2 else 'Mid' if count <= 5 else 'Senior'
    return 'Unspecified'

def us_location(location, states):
    if re.search(r"United Kingdom|Canada|Australia|India|Germany|France", location, re.I):
        return False
    if re.search(r"United States|\bUSA\b|\bUS\b", location, re.I) and not states:
        return True
    choices = {code: STATES[code] for code in states} if states else STATES
    for code, name in choices.items():
        if re.search(r"\b" + re.escape(name) + r"\b", location, re.I):
            return True
        # Abbreviations need a location delimiter or an uppercase standalone value.
        if location.strip() == code or re.search(r"(?:,\s*|^US,\s*)" + code + r"(?=\b)", location):
            return True
    return False
