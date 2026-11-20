"""Public IT job search dashboard."""
import html
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

def apply_theme(dark):
    colors = {
        'background': '#0c1422' if dark else '#f4f7fb',
        'panel': '#152237' if dark else '#ffffff',
        'field': '#1c2d46' if dark else '#edf2f8',
        'text': '#edf3fc' if dark else '#182b45',
        'muted': '#a7b8d0' if dark else '#536780',
        'border': '#2c3e58' if dark else '#dbe4f0',
        'accent': '#a5b4fc' if dark else '#4338ca',
    }
    st.markdown("""
    <style>
    .stApp {--bg:BACKGROUND;--panel:PANEL;--field:FIELD;--ink:TEXT;--muted:MUTED;--line:BORDER;--accent:ACCENT;
        background:var(--bg);color:var(--ink);font-family:'Inter','Segoe UI',sans-serif;}
    [data-testid="stHeader"] {background:var(--bg);}
    [data-testid="stSidebar"] {background:var(--panel);border-right:1px solid var(--line);}
    [data-testid="stMainBlockContainer"] {max-width:1200px;padding-top:2.5rem;padding-bottom:4rem;}
    .stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,
    .stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stWidgetLabel"] {color:var(--ink);}
    .stApp [data-testid="stCaptionContainer"] p {color:var(--muted);}
    .stApp [data-baseweb="select"] > div,.stApp [data-baseweb="input"],
    .stApp input {background:var(--field);color:var(--ink);border-color:var(--line);}
    .stApp [data-baseweb="tag"] {background:var(--field);color:var(--ink);border:1px solid var(--line);}
    .stApp [data-testid="stForm"] {border:0;padding:0;}
    .stApp [data-testid="stVerticalBlockBorderWrapper"] {border-color:var(--line)!important;border-radius:18px;}
    .stApp [data-testid="stVerticalBlockBorderWrapper"] > div {background:var(--panel);border-radius:18px;}
    .stApp [data-testid="stBaseButton-primary"] {background:#4f46e5;border:1px solid #4f46e5;color:white;border-radius:10px;}
    .stApp [data-testid="stBaseButton-primary"] p {color:white;}
    .stApp [data-testid="stLinkButton"] a {background:var(--field);color:var(--accent);border:1px solid var(--line);border-radius:10px;}
    .stApp [data-testid="stLinkButton"] a p {color:var(--accent);}
    .hero {padding:2.4rem;border:1px solid var(--line);border-radius:24px;background:var(--panel);margin-bottom:1.5rem;}
    .hero h1 {font-size:clamp(2rem,4vw,3rem);letter-spacing:-.045em;margin:0 0 .6rem;line-height:1.1;}
    .hero p {margin:0;color:var(--muted);font-size:1rem;max-width:40rem;}
    .job-company {font-size:.88rem;color:var(--muted);margin-bottom:.45rem;}
    .job-title {font-size:1.15rem;font-weight:650;line-height:1.4;margin-bottom:.65rem;overflow-wrap:anywhere;}
    .job-location {font-size:.9rem;color:var(--muted);margin-bottom:.7rem;}
    .job-level {display:inline-block;border-radius:20px;background:var(--field);color:var(--accent);padding:.25rem .7rem;font-size:.78rem;margin-bottom:.65rem;}
    @media(max-width:640px){.hero{padding:1.4rem;}[data-testid="stMainBlockContainer"]{padding-top:1.5rem;}}
    </style>
    """.replace('BACKGROUND', colors['background']).replace('PANEL', colors['panel'])
        .replace('FIELD', colors['field']).replace('TEXT', colors['text'])
        .replace('MUTED', colors['muted']).replace('BORDER', colors['border'])
        .replace('ACCENT', colors['accent']), unsafe_allow_html=True)

def main():
    st.set_page_config(page_title='Career Launch Agent', page_icon='🧭',
                       layout='wide', initial_sidebar_state='expanded')
    with st.sidebar:
        st.markdown('### Career Launch Agent')
        theme = st.selectbox('Appearance', ['Light', 'Dark'], key='appearance')
    apply_theme(theme == 'Dark')
    with st.sidebar:
        st.divider()
        st.markdown('### Find your next role')
        with st.form('job_filters', border=False):
            keyword = st.text_input('Keyword or city', placeholder='Job title, skill, or city')
            scope = st.selectbox('Search area', ['Anywhere in the US', 'Selected states'])
            states = st.multiselect('States', list(STATES), default=['NC', 'SC'],
                                    format_func=lambda code: f'{STATES[code]} ({code})',
                                    help='Used when Search area is Selected states.')
            location_type = st.selectbox('Work location',
                                        ['Site-based', 'Include US remote', 'US remote only'])
            groups = st.multiselect('IT roles', list(ROLE_GROUPS), default=list(ROLE_GROUPS))
            levels = st.multiselect('Career level', LEVELS + ['Unspecified'],
                                    default=LEVELS + ['Unspecified'],
                                    help='Estimated from titles and employer data. Unspecified keeps unclear levels in your results.')
            employers = st.multiselect('Employers',
                                      sorted({board['company'] for board in CONFIG['boards']}),
                                      placeholder='All configured employers')
            submitted = st.form_submit_button('Find IT jobs', type='primary', use_container_width=True)
        st.caption('Searches configured employer boards. Check the original posting for qualifications and remote eligibility.')
    st.markdown('<div class="hero"><h1>Your next chapter in IT.</h1>'
                '<p>Explore opportunities across the US. Choose your location, career level, and the work you want to do.</p></div>',
                unsafe_allow_html=True)
    if submitted:
        selected_states = states if scope == 'Selected states' else []
        if not groups or not levels or (scope == 'Selected states' and not states and location_type != 'US remote only'):
            st.warning('Select IT roles, career levels, and states when using Selected states.')
            return
        with st.spinner('Finding opportunities on employer boards…'):
            jobs, warnings = public_jobs(tuple(selected_states))
            results = filter_jobs(jobs, selected_states, groups, location_type,
                                  employers, keyword.strip(), levels)
        st.session_state['job_results'] = (results, warnings)
    if 'job_results' not in st.session_state:
        st.subheader('Where would you like to go next?')
        st.write('Set your preferences in the filter panel, then select **Find IT jobs**.')
        return
    results, warnings = st.session_state['job_results']
    if warnings:
        st.warning('Some sources are unavailable. Results may be incomplete.')
        with st.expander('View source details'):
            st.write(', '.join(warnings))
    if not results:
        if len(warnings) == len(CONFIG['boards']):
            st.error('Employer boards are unavailable. Please try again later.')
        else:
            st.subheader('No matches this time')
            st.write('Try another career level, a broader location, or fewer keywords.')
        return
    st.subheader(f'{len(results)} matching {"opportunity" if len(results) == 1 else "opportunities"}')
    st.caption('Career levels are estimated. Review full requirements on the employer’s page.')
    for offset in range(0, len(results), 2):
        columns = st.columns(2, gap='medium')
        for column, job in zip(columns, results[offset:offset + 2]):
            with column, st.container(border=True):
                st.markdown(
                    '<div class="job-company">' + html.escape(job['company']) + '</div>'
                    '<div class="job-title">' + html.escape(job['title']) + '</div>'
                    '<div class="job-location">' + html.escape(job['location']) + '</div>'
                    '<span class="job-level">' + html.escape(career_level(job)) + '</span>',
                    unsafe_allow_html=True)
                st.link_button('View employer posting ↗', job['url'], use_container_width=True)

if __name__ == '__main__':
    main()
