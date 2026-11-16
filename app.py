"""Public IT job search dashboard."""
import streamlit as st

from career import CONFIG, search
from job_sources import canonical, contains, location_matches

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
def public_jobs():
    return search()

def filter_jobs(jobs, states, groups, location_type, employers, keyword):
    titles = tuple(term for group in groups for term in ROLE_GROUPS[group])
    location_config = {'locations': states, 'include_remote': location_type != 'NC/SC site-based'}
    results = {}
    for job in jobs:
        if employers and job['company'] not in employers:
            continue
        location = job['location']
        remote = contains(location, 'remote')
        if location_type == 'US remote only' and not remote:
            continue
        if not location_matches(location, location_config):
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
    st.title('Career Launch Agent')
    st.caption('Find IT openings and apply through the employer’s careers page.')
    with st.form('job_filters'):
        left, right = st.columns(2)
        with left:
            states = st.multiselect('States', ['NC', 'SC'], default=['NC', 'SC'])
            groups = st.multiselect('IT roles', list(ROLE_GROUPS), default=list(ROLE_GROUPS))
        with right:
            location_type = st.selectbox('Work location', ['NC/SC site-based', 'NC/SC plus US remote', 'US remote only'])
            companies = sorted({board['company'] for board in CONFIG['boards']})
            employers = st.multiselect('Employers', companies, placeholder='All configured employers')
        keyword = st.text_input('Keyword or city (optional)', placeholder='Windows, Charlotte, CompTIA A+')
        submitted = st.form_submit_button('Find IT jobs', type='primary')
    if submitted:
        if not groups or (not states and location_type != 'US remote only'):
            st.warning('Select at least one IT role and, for site-based jobs, at least one state.')
            return
        with st.spinner('Checking employer boards…'):
            jobs, warnings = public_jobs()
            results = filter_jobs(jobs, states, groups, location_type, employers, keyword.strip())
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
                st.caption(f"{job['company']} · {job['location']}")
                st.link_button('View employer posting', job['url'])

if __name__ == '__main__':
    main()
