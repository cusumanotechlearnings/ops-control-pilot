"""
Marketing Ops AI -- Seed Data Generator
Generates ~80k rows of realistic dummy data modeled after SFMC structure
Run: python 02_seed_data.py
Requires: pip install psycopg2-binary faker python-dotenv
"""

import random
import uuid
import os
from datetime import datetime, timedelta, date
from faker import Faker
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()
fake = Faker()
random.seed(42)

# ── connection ──────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")  # set in .env as Neon connection string

# ── constants ───────────────────────────────────────────────
BUSINESS_UNITS = ['UC', 'GC', 'OL', 'MIL', 'INTL']
JOURNEY_STATUSES = ['Active', 'Stopped', 'Draft', 'Paused', 'Complete']
STUDENT_STAGES = ['Inquiry', 'Applicant', 'Admitted', 'Enrolled', 'Alumni', 'Stopped']
STUDENT_TYPES = ['Military', 'International', 'Domestic', 'Transfer']
STUDENT_LEVELS = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate', 'Doctoral']
DEPARTMENTS = ['SFS', 'Advising', 'Admissions', 'FA', 'Registrar', 'Housing', 'Career']
SEGMENTS = ['Military', 'International', 'Freshman', 'Senior', 'Graduate',
            'Campus', 'Transfer', 'Alumni', 'Inquiry']
TERM_CODES = ['23FA', '24SP', '24FA', '25SP', '25FA']
IMAGE_TYPES = ['hero', 'banner', 'icon', 'cta', 'background']
IMAGE_SUBJECTS = ['campus', 'student', 'graduation', 'financial', 'abstract', 'faculty']
COLORS = ['blue', 'red', 'green', 'neutral', 'purple', 'orange']

ACADEMIC_TERMS = [
    ('23FA', 'Fall 2023',  '2023-09-01', '2023-12-20', 'FY2024', 'Fall'),
    ('24SP', 'Spring 2024','2024-01-15', '2024-05-10', 'FY2024', 'Spring'),
    ('24FA', 'Fall 2024',  '2024-09-01', '2024-12-20', 'FY2025', 'Fall'),
    ('25SP', 'Spring 2025','2025-01-15', '2025-05-10', 'FY2025', 'Spring'),
    ('25FA', 'Fall 2025',  '2025-09-01', '2025-12-20', 'FY2026', 'Fall'),
]

EMAIL_TEMPLATES = [
    ('EM-SFS-UC-FAFSA-Available',           'SFS', 'UC',   'Complete your FAFSA today'),
    ('EM-SFS-UC-Federal_Work_Study',         'SFS', 'UC',   "You've been offered work-study, now what"),
    ('EM-SFS-UC-Health_Insurance_Waiver',    'SFS', 'UC',   'Do you need school health insurance?'),
    ('EM-FA100-FA_AWD_CFP-MIL',             'FA',  'MIL',  'Important Information | College Financing Plans'),
    ('EM-UC-AV-Add_Drop_Update',            'Advising','UC','Important Update | Add/Drop Ends'),
    ('EM-UC-AV-UG-Final_Grades_Available',  'Advising','UC','Final grades now available'),
    ('EM-UC-AV-Registration-Reminder',      'Advising','UC','Time to register for next term'),
    ('EM-OL-ADM-Application-Received',      'Admissions','OL','We received your application'),
    ('EM-OL-ADM-Application-Decision',      'Admissions','OL','Your admission decision is ready'),
    ('EM-MIL-SFS-VA-Benefits-Info',         'SFS', 'MIL',  'Your VA benefits information'),
    ('EM-INTL-ADM-Visa-Requirements',       'Admissions','INTL','Important visa requirement information'),
    ('EM-GC-AV-Commencement-Info',          'Advising','GC', 'Commencement ceremony details'),
    ('EM-UC-REG-Transcript-Request',        'Registrar','UC','How to request your transcript'),
    ('EM-UC-HSG-Housing-Application',       'Housing','UC', 'Housing application now open'),
    ('EM-UC-CAR-Internship-Opportunities',  'Career','UC',  'New internship opportunities available'),
    ('EM-GC-ADM-Program-Info',              'Admissions','GC','Graduate program information'),
    ('EM-OL-SFS-Payment-Plan',              'SFS', 'OL',   'Payment plan options available'),
    ('EM-MIL-ADM-TA-Benefits',              'Admissions','MIL','Tuition Assistance benefit guide'),
    ('EM-INTL-SFS-Scholarship-Info',        'SFS', 'INTL', 'International scholarship opportunities'),
    ('EM-UC-AV-Academic-Standing',          'Advising','UC','Important: Your academic standing'),
]

SMS_TEMPLATES = [
    ('SMS-UC-REG-Reminder',   'UC',   'Registration opens tomorrow. Log in to mySNHU to register.'),
    ('SMS-MIL-SFS-Deadline',  'MIL',  'Your VA benefit paperwork deadline is in 3 days.'),
    ('SMS-OL-ADM-Decision',   'OL',   'Your admissions decision is ready. Check your email!'),
    ('SMS-UC-EVT-OpenHouse',  'UC',   'Campus Open House this Saturday 10am-3pm. See you there!'),
    ('SMS-GC-AV-Grades',      'GC',   'Final grades are now posted in mySNHU.'),
]

def rand_date(start_year=2023, end_year=2025):
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def rand_ts(start_year=2023, end_year=2025):
    d = rand_date(start_year, end_year)
    return datetime(d.year, d.month, d.day,
                    random.randint(6,18), random.randint(0,59))

def rand_rate(base, spread=0.08):
    return round(max(0, min(1, base + random.gauss(0, spread))), 6)

# ────────────────────────────────────────────────────────────

def seed(conn):
    cur = conn.cursor()

    # 1 ── academic_terms ────────────────────────────────────
    print("Seeding academic_terms...")
    execute_values(cur, """
        INSERT INTO academic_terms
            (term_code,term_name,term_start_date,term_end_date,academic_year,season)
        VALUES %s ON CONFLICT DO NOTHING
    """, ACADEMIC_TERMS)

    # 2 ── email_assets ──────────────────────────────────────
    print("Seeding email_assets...")
    email_rows = []
    email_asset_ids = []
    for i, (name, dept, bu, subject) in enumerate(EMAIL_TEMPLATES):
        asset_id = f"EA-{10000+i}"
        email_asset_ids.append(asset_id)
        created = rand_ts(2022, 2023)
        modified = created + timedelta(days=random.randint(0, 300))
        email_rows.append((
            asset_id, f"LEG-{90000+i}", f"20250928_{350000+i}",
            bu, name, subject,
            fake.sentence(nb_words=8),
            'templatebasedemail', '207',
            f"Folder/{dept}",
            dept,
            f"{dept.lower()}@snhu.edu",
            f"Student {dept}",
            fake.paragraph(nb_sentences=4),
            fake.name(), fake.email(),
            fake.name(), fake.email(),
            created, modified,
            str(uuid.uuid4())
        ))
    execute_values(cur, """
        INSERT INTO email_assets
            (asset_id,legacy_id,unique_id,business_unit,name,subject_line,
             pre_header,asset_type_name,asset_type_id,folder,department_code,
             sender_address,sender_name,copy_found,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date,object_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, email_rows)

    # 3 ── image_assets ──────────────────────────────────────
    print("Seeding image_assets...")
    image_rows = []
    image_urls = [
        "https://client-data.knak.io/production/email_assets/5fd10b569d941/Y9PaAR4BN1uvwQSeUR37Jtdwa2YUrN1By1RZIsk8.png",
        "https://client-data.knak.io/production/email_assets/5fd10b569d941/VMCCefovhhRHSaoumU0KPjByRgg2JPzU6kiQl1cI.png",
        "https://image.dream.snhu.edu/lib/fe9113737461067571/m/1/65052196-4d4e-435d-82a7-e84e2edcc1f3.png",
    ]
    for i in range(60):
        url = random.choice(image_urls) if i < 3 else f"https://image.dream.snhu.edu/assets/{uuid.uuid4()}.png"
        email_id = random.choice(email_asset_ids) if random.random() > 0.3 else None
        ctr_base = random.uniform(0.01, 0.12)
        or_base  = random.uniform(0.18, 0.45)
        image_rows.append((
            url, email_id,
            random.choice(IMAGE_TYPES),
            random.choice(IMAGE_SUBJECTS),
            random.choice(COLORS),
            random.random() > 0.4,
            random.random() > 0.6,
            random.randint(50, 800),
            random.choice([600,800,1200]),
            random.choice([300,400,600]),
            round(ctr_base, 4),
            round(or_base, 4),
            random.randint(1, 25),
            random.choice(BUSINESS_UNITS)
        ))
    execute_values(cur, """
        INSERT INTO image_assets
            (image_url,email_asset_id,image_type,subject_matter,primary_color,
             has_people,has_text_overlay,file_size_kb,width_px,height_px,
             avg_click_rate,avg_open_rate,usage_count,business_unit)
        VALUES %s
    """, image_rows)

    # 4 ── sms_assets ────────────────────────────────────────
    print("Seeding sms_assets...")
    sms_asset_ids = []
    sms_rows = []
    for i, (name, bu, msg) in enumerate(SMS_TEMPLATES):
        aid = f"SMS-{20000+i}"
        sms_asset_ids.append(aid)
        created = rand_ts(2023, 2024)
        sms_rows.append((
            aid, bu, name, msg,
            f"KW-{random.randint(1000,9999)}",
            f"8{random.randint(1000,9999)}",
            'US', True,
            fake.name(), fake.email(),
            fake.name(), fake.email(),
            created, created + timedelta(days=random.randint(0,180))
        ))
    execute_values(cur, """
        INSERT INTO sms_assets
            (asset_id,business_unit,name,message_text,keyword_id,short_code,
             country_code,opt_in_configured,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, sms_rows)

    # 5 ── content_block_assets ──────────────────────────────
    print("Seeding content_block_assets...")
    cb_rows = []
    for i in range(30):
        aid = f"CB-{30000+i}"
        created = rand_ts(2022, 2023)
        cb_rows.append((
            aid, f"20250928_CB{i}",
            random.choice(BUSINESS_UNITS),
            f"CB-{fake.word().title()}-Block-{i}",
            'contentblock',
            random.choice(['Footer', 'Header', 'Disclaimer', 'CTA', 'Navigation']),
            str(random.randint(10000,99999)),
            '1',
            fake.paragraph(nb_sentences=2),
            fake.name(), fake.email(),
            fake.name(), fake.email(),
            created, created + timedelta(days=random.randint(0,200))
        ))
    execute_values(cur, """
        INSERT INTO content_block_assets
            (asset_id,unique_id,business_unit,name,asset_type_name,
             folder_name,folder_id,version,copy_found,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, cb_rows)

    # 6 ── landing_page_assets ───────────────────────────────
    print("Seeding landing_page_assets...")
    lp_rows = []
    lp_names = [
        ('UC-TRA-Accept',      'UC', 'https://cloud.dream.snhu.edu/UC-TRA-Accept',      'Published'),
        ('UC-First-Year-Accept','UC','https://cloud.dream.snhu.edu/UC-First-Year-Accept','Published'),
        ('OL-INQ-Landing',     'OL', 'https://cloud.dream.snhu.edu/OL-INQ',             'Published'),
        ('MIL-TA-Benefits',    'MIL','https://cloud.dream.snhu.edu/MIL-TA',             'Published'),
        ('GC-Program-Finder',  'GC', 'https://cloud.dream.snhu.edu/GC-Programs',        'Draft'),
        ('INTL-Admissions',    'INTL','https://cloud.dream.snhu.edu/INTL-Admissions',   'Published'),
    ]
    for i, (pname, bu, url, status) in enumerate(lp_names):
        aid = f"LP-{40000+i}"
        created = rand_ts(2023, 2024)
        pub_date = created + timedelta(days=random.randint(1,14)) if status == 'Published' else None
        lp_rows.append((
            aid, f"20250928_LP{i}", bu, pname, pname, url,
            status, 'landingpage', 'Nurture - Dev', '1',
            pub_date, fake.paragraph(nb_sentences=3), True, True, True,
            fake.name(), fake.email(),
            fake.name(), fake.email(),
            created, created + timedelta(days=random.randint(0,300))
        ))
    execute_values(cur, """
        INSERT INTO landing_page_assets
            (asset_id,unique_id,business_unit,name,page_name,page_url,
             published_status,asset_type_name,folder,version,
             published_date,copy_found,has_form,
             has_google_analytics,has_google_tag_manager,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, lp_rows)

    # 7 ── automations ────────────────────────────────────────
    print("Seeding automations...")
    auto_ids = []
    auto_rows = []
    auto_templates = [
        ('AU-UC-INTL-APP-AIP-ACC-FY25-July', 'UC',   'Scheduled', 'Paused'),
        ('Adhoc-AU-UC-FY-ACC-Deposit-Deadline-25FA','UC','Scheduled','Paused'),
        ('AU-MIL-SFS-VA-Benefits-Weekly',    'MIL',  'Scheduled', 'Active'),
        ('AU-OL-ADM-Application-Daily',      'OL',   'Scheduled', 'Active'),
        ('AU-GC-AV-Commencement-YOY',        'GC',   'Scheduled', 'Active'),
        ('AU-UC-REG-Registration-Reminder',  'UC',   'Scheduled', 'Active'),
        ('AU-INTL-ADM-Visa-Weekly',          'INTL', 'Scheduled', 'Active'),
        ('AU-UC-SFS-FAFSA-Campaign-25FA',    'UC',   'Scheduled', 'Stopped'),
        ('AU-OL-INQ-NurtureFlow-Daily',      'OL',   'Scheduled', 'Active'),
        ('AU-MIL-ADM-TA-Benefits-Monthly',   'MIL',  'Scheduled', 'Active'),
    ]
    for i, (name, bu, atype, status) in enumerate(auto_templates):
        aid = str(uuid.uuid4())
        akey = str(uuid.uuid4())
        auto_ids.append(aid)
        last_run = rand_ts(2025, 2025)
        auto_rows.append((
            aid, akey, name, f"Automated send for {name}",
            bu, 1, atype, 4, status,
            random.randint(10000,99999),
            f"Daily {random.randint(6,10)}:00AM",
            last_run, str(uuid.uuid4())
        ))
    execute_values(cur, """
        INSERT INTO automations
            (automation_id,automation_key,name,description,
             business_unit,type_id,type,status_id,status,
             category_id,schedule,last_run_time,last_run_instance_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, auto_rows)

    # 8 ── journeys ──────────────────────────────────────────
    print("Seeding journeys...")
    journey_ids = []
    journey_rows = []
    journey_templates = [
        ('JB-FA100-FA_AWD_CFP-MIL-College-Financing-Plan','MIL','Stopped', 'Military','SFS',   '25FA'),
        ('JB-SFS-UC-Federal_Work_Study',                  'UC', 'Active',  'Campus',  'SFS',   '25FA'),
        ('JB-SFS-UC-Health_Insurance_Waiver',             'UC', 'Active',  'Campus',  'SFS',   '25FA'),
        ('JB-UC-AV-Add_Drop_Update',                      'UC', 'Stopped', 'Campus',  'Advising','25FA'),
        ('JB-UC-AV-Final_Grades',                         'UC', 'Active',  'Campus',  'Advising','25FA'),
        ('JB-UC-AV-Registration-Reminder-25FA',           'UC', 'Active',  'Freshman','Advising','25FA'),
        ('JB-OL-ADM-Application-Nurture',                 'OL', 'Active',  'Inquiry', 'Admissions','25FA'),
        ('JB-MIL-SFS-VA-Benefits-Onboard',               'MIL','Active',  'Military','SFS',   '25FA'),
        ('JB-INTL-ADM-Visa-Requirements',                 'INTL','Active', 'International','Admissions','25FA'),
        ('JB-GC-AV-Commencement-InPerson-Survey-YOY',    'GC', 'Active',  'Graduate','Advising','25SP'),
        ('JB-UC-SFS-FAFSA-Available-Incoming',            'UC', 'Stopped', 'Freshman','SFS',   '24FA'),
        ('JB-OL-SFS-Payment-Plan-Reminder',               'OL', 'Active',  'Enrolled','SFS',   '25FA'),
        ('JB-MIL-ADM-TA-Benefits-Guide',                  'MIL','Active',  'Military','Admissions','25FA'),
        ('JB-GC-ADM-Program-Info-Graduate',               'GC', 'Draft',   'Graduate','Admissions','25FA'),
        ('JB-UC-HSG-Housing-Application-25FA',            'UC', 'Active',  'Freshman','Housing','25FA'),
        ('UG-to-GR-Alumni-Push',                          'GC', 'Stopped', 'Alumni',  'Advising','24FA'),
        ('JB-INTL-SFS-Scholarship-Campaign',              'INTL','Active', 'International','SFS','25FA'),
        ('JB-UC-AV-Academic-Standing-Alert',              'UC', 'Active',  'Campus',  'Advising','25FA'),
        ('JB-OL-ADM-Deposit-Deadline-25FA',               'OL', 'Stopped', 'Applicant','Admissions','25FA'),
        ('JB-UC-CAR-Internship-Spring-25',                'UC', 'Active',  'Senior',  'Career', '25SP'),
    ]
    for i, (name, bu, status, audience, dept, term) in enumerate(journey_templates):
        jid = str(uuid.uuid4())
        jkey = str(uuid.uuid4())
        journey_ids.append(jid)
        created = rand_ts(2022, 2024)
        modified = created + timedelta(days=random.randint(1, 400))
        journey_rows.append((
            jid, jkey, name,
            f"Journey for {audience} audience - {dept} department",
            bu, status,
            random.randint(1, 3), 1.0,
            'SingleEntryAcrossAllVersions',
            str(uuid.uuid4()),
            modified, created,
            audience, dept, term
        ))
    execute_values(cur, """
        INSERT INTO journeys
            (journey_id,journey_key,journey_name,description,
             business_unit,status,version,workflow_api_version,
             entry_mode,event_definition_id,
             last_modified_date,created_date,
             target_audience,department,academic_term)
        VALUES %s ON CONFLICT DO NOTHING
    """, journey_rows)

    # 9 ── journey_entry_sources ─────────────────────────────
    print("Seeding journey_entry_sources...")
    jes_rows = []
    for i, jid in enumerate(journey_ids):
        etype = random.choice(['AutomationAudience','EmailAudience','Schedule'])
        auto_id = random.choice(auto_ids) if etype == 'AutomationAudience' else None
        start_ts = rand_ts(2024, 2025)
        jes_rows.append((
            str(uuid.uuid4()), jid,
            journey_templates[i][0], journey_templates[i][1],
            etype, f"JB-EV-{journey_templates[i][0][:30]}",
            str(uuid.uuid4()), str(uuid.uuid4()),
            f"DE-{journey_templates[i][0][:40]}",
            auto_id,
            'Production',
            random.choice(['Daily','Weekly','Once']),
            start_ts,
            start_ts + timedelta(days=random.randint(30,365)),
            random.randint(1,7),
            fake.name(), fake.name()
        ))
    execute_values(cur, """
        INSERT INTO journey_entry_sources
            (entry_source_id,journey_id,journey_name,business_unit,
             entry_type,event_definition_key,
             event_definition_id,data_extension_id,data_extension_name,
             automation_id,mode,schedule_frequency,
             schedule_start_time,schedule_end_time,schedule_occurrences,
             created_by,last_modified_by)
        VALUES %s ON CONFLICT DO NOTHING
    """, jes_rows)

    # 10 ── journey_activities ────────────────────────────────
    print("Seeding journey_activities...")
    act_rows = []
    jact_ids_for_metrics = []
    for i, (jid, (jname, bu, jstatus, audience, dept, term)) in enumerate(
            zip(journey_ids, journey_templates)):
        # 1-3 email activities per journey
        num_emails = random.randint(1, 3)
        for step in range(num_emails):
            aid = str(uuid.uuid4())
            email_template = random.choice(EMAIL_TEMPLATES)
            email_id_idx = EMAIL_TEMPLATES.index(email_template)
            email_asset_ref = email_asset_ids[email_id_idx]
            send_status_val = 'Active' if jstatus == 'Active' else 'Stopped'
            jact_ids_for_metrics.append((
                aid, jid, jname, bu, email_asset_ref,
                email_template[0], email_template[2], audience, dept
            ))
            act_rows.append((
                aid, jid, jname,
                f"EMAILV2-{step+1}",
                bu,
                f"Email Step {step+1}: {email_template[0][:40]}",
                'EMAIL',
                email_asset_ref, email_template[0], email_template[2],
                email_template[3],
                send_status_val,
                str(uuid.uuid4()), str(uuid.uuid4()),
                True, True, True,
                f"GA-{jname[:30]}-step{step+1}",
                fake.name(), rand_ts(2023, 2024)
            ))
        # optional SMS activity
        if random.random() > 0.6 and sms_asset_ids:
            sms_aid = str(uuid.uuid4())
            sms_ref = random.choice(sms_asset_ids)
            act_rows.append((
                sms_aid, jid, jname,
                'SMS-1',
                bu,
                f"SMS Step: {jname[:40]}",
                'SMS',
                None, None, None, None, None, None, None,
                False, False, False,
                f"GA-{jname[:30]}-sms",
                fake.name(), rand_ts(2023, 2024)
            ))
    execute_values(cur, """
        INSERT INTO journey_activities
            (activity_id,journey_id,journey_name,activity_key,business_unit,
             activity_name,activity_type,
             email_id,email_name,email_subject,email_pre_header,
             send_status,send_key,triggered_send_id,
             salesforce_tracking,send_logging,click_tracking,
             ga_campaign_name,last_modified_by,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, act_rows)

    # 11 ── subscribers ──────────────────────────────────────
    print("Seeding subscribers (~5000 records)...")
    sub_rows = []
    sub_keys = []
    for i in range(5000):
        sk = f"SUB-{100000+i}"
        sub_keys.append(sk)
        bu = random.choice(BUSINESS_UNITS)
        stype = random.choice(STUDENT_TYPES)
        slevel = random.choice(STUDENT_LEVELS)
        stage = random.choice(STUDENT_STAGES)
        term = random.choice(TERM_CODES)
        sub_rows.append((
            sk,
            f"COL-{random.randint(1000000,9999999)}",
            fake.email(),
            fake.first_name(), fake.last_name(),
            fake.first_name() if random.random() > 0.3 else None,
            bu, stage, stype, slevel,
            bu[:2], bu[:2], 'UG' if slevel in ['Freshman','Sophomore','Junior','Senior'] else 'GR',
            term,
            rand_ts(2022, 2025),
            f"POPSEL-{bu}-{stype[:3].upper()}-{term}",
            random.random() > 0.1
        ))
    execute_values(cur, """
        INSERT INTO subscribers
            (subscriber_key,colleague_id,email,first_name,last_name,
             preferred_first_name,business_unit,student_stage,student_type,
             student_level,campus,original_campus,level,admit_term,
             term_start_date,popsel_name,is_active_subscriber)
        VALUES %s ON CONFLICT DO NOTHING
    """, sub_rows)

    # 12 ── opportunities ─────────────────────────────────────
    print("Seeding opportunities (~4000 records)...")
    enrolled_keys = random.sample(sub_keys, 4000)
    opp_rows = []
    programs = [
        'Business Administration', 'Computer Science', 'Psychology',
        'Healthcare Administration', 'Criminal Justice', 'Communication',
        'Information Technology', 'Accounting', 'Marketing', 'Education'
    ]
    for sk in enrolled_keys:
        term = random.choice(TERM_CODES)
        stage = random.choice(['Application', 'Admitted', 'Enrolled', 'Registered'])
        opp_rows.append((
            sk,
            f"COL-{random.randint(1000000,9999999)}",
            stage,
            random.choice(programs),
            random.choice(['UG', 'GR']),
            term,
            term if stage == 'Enrolled' else None,
            random.random() > 0.3,
            random.random() > 0.9,
            round(random.uniform(1.8, 4.0), 2)
        ))
    execute_values(cur, """
        INSERT INTO opportunities
            (subscriber_key,colleague_id,stage_name,program_name,
             program_level,admit_term,enrolled_term,
             registered_next_term,withdrew,gpa)
        VALUES %s
    """, opp_rows)

    # 13 ── dod_metrics (the big one) ─────────────────────────
    print("Seeding dod_metrics (~70000 rows)... this may take a minute")
    metrics_rows = []
    base_open_rates = {
        'Military': 0.38, 'International': 0.32, 'Freshman': 0.29,
        'Senior': 0.27, 'Graduate': 0.31, 'Campus': 0.28,
        'Transfer': 0.26, 'Alumni': 0.22, 'Inquiry': 0.24,
    }
    # For each journey activity, generate daily metrics over a date range
    for act_info in jact_ids_for_metrics:
        act_id, jid, jname, bu, email_ref, email_name, subject, audience, dept = act_info
        base_or  = base_open_rates.get(audience, 0.28)
        base_ctr = base_or * random.uniform(0.25, 0.45)
        # 30-90 days of send history
        num_days = random.randint(30, 90)
        start_d  = rand_date(2024, 2025)
        for day_offset in range(num_days):
            send_dt = start_d + timedelta(days=day_offset)
            sends   = random.randint(200, 3000)
            deliv   = int(sends * rand_rate(0.97, 0.01))
            opens   = int(deliv * rand_rate(base_or, 0.05))
            u_opens = int(opens * rand_rate(0.75, 0.08))
            clicks  = int(u_opens * rand_rate(base_ctr * 2, 0.04))
            u_clk   = int(clicks * rand_rate(0.70, 0.08))
            bounces = sends - deliv
            unsubs  = max(0, int(sends * rand_rate(0.002, 0.001)))
            or_calc  = round(u_opens / deliv, 6) if deliv > 0 else 0
            ctr_calc = round(u_clk   / deliv, 6) if deliv > 0 else 0
            dr_calc  = round(deliv   / sends, 6) if sends > 0 else 0
            ctor     = round(u_clk   / u_opens, 6) if u_opens > 0 else 0
            br_calc  = round(bounces / sends, 6) if sends > 0 else 0
            job_id   = str(random.randint(3000000, 3999999))
            metrics_rows.append((
                job_id,
                f"{email_name}{send_dt.strftime('%b %d %Y %I:%M%p')}",
                f"{email_name}_{job_id}_{send_dt.strftime('%Y%m%d')}",
                bu, email_name, email_ref,
                jname, jid, 'Active' if random.random() > 0.3 else 'Stopped',
                random.randint(1,3),
                f"{jid}_{random.randint(1,3)}",
                f"{dept.lower()}@snhu.edu",
                f"Student {dept}",
                subject,
                send_dt,
                sends, deliv, bounces, opens, u_opens,
                clicks, u_clk, unsubs,
                or_calc, ctr_calc, dr_calc, ctor, br_calc,
                audience, dept
            ))
            # batch insert every 5000
            if len(metrics_rows) >= 5000:
                execute_values(cur, """
                    INSERT INTO dod_metrics
                        (job_id,id_combo,unique_email_send,
                         business_unit,email_name,email_asset_id,
                         journey_name,journey_id,journey_status,
                         journey_version,unique_journey_id_version,
                         sender_address,sender_name,subject_line,
                         send_date,
                         total_sends,deliveries,total_bounces,
                         total_opens,unique_opens,total_clicks,unique_clicks,
                         total_unsubscribes,
                         open_rate,click_rate,delivery_rate,
                         click_to_open_rate,bounce_rate,
                         target_segment,department_code)
                    VALUES %s
                """, metrics_rows)
                conn.commit()
                metrics_rows = []
                print(f"  ...{day_offset} days processed for current batch")

    # flush remaining
    if metrics_rows:
        execute_values(cur, """
            INSERT INTO dod_metrics
                (job_id,id_combo,unique_email_send,
                 business_unit,email_name,email_asset_id,
                 journey_name,journey_id,journey_status,
                 journey_version,unique_journey_id_version,
                 sender_address,sender_name,subject_line,
                 send_date,
                 total_sends,deliveries,total_bounces,
                 total_opens,unique_opens,total_clicks,unique_clicks,
                 total_unsubscribes,
                 open_rate,click_rate,delivery_rate,
                 click_to_open_rate,bounce_rate,
                 target_segment,department_code)
            VALUES %s
        """, metrics_rows)

    conn.commit()
    cur.close()
    print("\n✅ Seed complete!")

    # row counts
    cur2 = conn.cursor()
    for tbl in ['academic_terms','email_assets','sms_assets','content_block_assets',
                'landing_page_assets','image_assets','automations','journeys',
                'journey_entry_sources','journey_activities','subscribers',
                'opportunities','dod_metrics']:
        cur2.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl}: {cur2.fetchone()[0]:,} rows")
    cur2.close()


if __name__ == "__main__":
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        print("    Format: postgresql://user:pass@host/dbname?sslmode=require")
        exit(1)
    conn = psycopg2.connect(DATABASE_URL)
    seed(conn)
    conn.close()
