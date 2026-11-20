"""Public IT job search dashboard."""
import streamlit as st

from career import CONFIG, search
from job_sources import canonical, contains
from filters import STATES, LEVELS, career_level, us_location

ROLE_GROUPS = {
    'Help desk and desktop support': (
        'help desk', 'helpdesk', 'service desk', 'desktop support', 'desktop technician',
        'IT support', 'IT technician', 'IT field technician', 'IT specialist',
        'technical support', 'computer technician', 'PC technician', 'support technician',
        'field support', 'instructional support technician', 'end user support',
        'deployment technician',
    ),
    'Networking': ('network technician', 'network support', 'network engineer', 'network administrator', 'NOC'),
    'Data center': ('data center technician', 'datacenter technician', 'data center operations', 'datacenter operations'),
    'Systems and cloud': ('systems support', 'systems administrator', 'system administrator',
                          'systems engineer', 'cloud support', 'cloud engineer', 'IT operations', 'IT analyst'),
    'Cybersecurity': ('cybersecurity', 'cyber security', 'information security', 'SOC analyst', 'security engineer'),
}

@st.cache_data(ttl=900, show_spinner=False)
def public_jobs(states):
    return search(states=list(states))

def filter_jobs(jobs, states, groups, location_type, employers, keyword, levels=None):
    titles = tuple(term for group in groups for term in ROLE_GROUPS[group])
    results = {}
    for job in jobs:
        if employers and job['company'] not in employers:
            continue
        location = job['location']
        remote = contains(location, 'remote')
        if location_type == 'US remote only' and not remote:
            continue
        if remote and location_type == 'Site-based':
            continue
        if not us_location(location, [] if remote else states):
            continue
        if levels and career_level(job) not in levels:
            continue
        if not any(contains(job['title'], title) for title in titles):
            continue
        searchable = ' '.join(job[key] for key in ('title', 'company', 'location', 'description'))
        if keyword and keyword.casefold() not in searchable.casefold():
            continue
        try:
            url = canonical(job['url'])
        except (TypeError, ValueError):
            continue
        results.setdefault(url, dict(job, url=url))
    return sorted(results.values(), key=lambda job: (job['title'].casefold(), job['company'].casefold(), job['url']))

def main():
    st.set_page_config(page_title='Career Launch Agent', page_icon='🧭', layout='wide')
    theme = st.selectbox('Theme', ['Light', 'Dark'], key='appearance')
    dark = theme == 'Dark'
    background, panel, text = ('#101827', '#1c293d', '#f1f5f9') if dark else ('#ffffff', '#f1f5f9', '#142033')
    st.markdown(f'''<style>
    .stApp, [data-testid="stHeader"] {{background-color:{background}; color:{text}; color-scheme:{theme.lower()};}}
    .stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stText"] {{color:{text};}}
    .stApp [data-baseweb="select"] > div, .stApp input, .stApp button,
    .stApp [data-testid="stForm"], .stApp [data-testid="stVerticalBlockBorderWrapper"] {{background-color:{panel}; color:{text};}}
    .stApp a {{color:{'#93c5fd' if dark else '#1456ab'};}}
    </style>''', unsafe_allow_html=True)
    st.title('Career Launch Agent')
    st.caption('Find IT openings and apply through the employer’s careers page.')
    with st.form('job_filters'):
        left, right = st.columns(2)
        with left:
            scope = st.selectbox('Search area', ['Anywhere in the US', 'Selected states'])
            states = st.multiselect('States', list(STATES), default=['NC', 'SC'],
                                    format_func=lambda code: f'{STATES[code]} ({code})',
                                    help='Applied when Search area is Selected states.')
            groups = st.multiselect('IT roles', list(ROLE_GROUPS), default=list(ROLE_GROUPS))
        with right:
            location_type = st.selectbox('Work location', ['Site-based', 'Include US remote', 'US remote only'])
            companies = sorted({board['company'] for board in CONFIG['boards']})
            employers = st.multiselect('Employers', companies, placeholder='All configured employers')
        levels = st.multiselect('Career level', LEVELS + ['Unspecified'],
                                default=LEVELS + ['Unspecified'])
        keyword = st.text_input('Keyword or city (optional)', placeholder='Windows, Charlotte, CompTIA A+')
        submitted = st.form_submit_button('Find IT jobs', type='primary')
    st.caption('Career levels are estimated from employer metadata, titles, and stated minimum experience. Unspecified includes postings without clear level information.')
    if submitted:
        selected_states = states if scope == 'Selected states' else []
        if not groups or not levels or (scope == 'Selected states' and not states and location_type != 'US remote only'):
            st.warning('Select IT roles, career levels, and states when using Selected states.')
            return
        with st.spinner('Checking employer boards…'):
            jobs, warnings = public_jobs(tuple(selected_states))
            results = filter_jobs(jobs, selected_states, groups, location_type, employers, keyword.strip(), levels)
        st.session_state['job_results'] = (results, warnings)
    if 'job_results' in st.session_state:
        results, warnings = st.session_state['job_results']
        if warnings:
            st.warning('Sources unavailable: ' + ', '.join(warnings))
        if not results:
            if len(warnings) == len(CONFIG['boards']):
                st.error('The configured employer boards are unavailable. Try again later.')
            else:
                st.info('No matching jobs from the available boards. Try a broader role or remove the keyword.')
            return
        st.subheader(f'{len(results)} matching {"job" if len(results) == 1 else "jobs"}')
        for job in results:
            with st.container(border=True):
                st.text(job['title'])
                st.caption(f"{job['company']} · {job['location']} · {career_level(job)}")
                st.link_button('View employer posting', job['url'])

if __name__ == '__main__':
    main()
