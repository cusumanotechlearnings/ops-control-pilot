"""
08_seed_draft_journeys.py — Avalon University Marketing Ops AI
Inserts 8 new scheduled DRAFT journeys with future schedule_start_time
(all on or after 2026-04-01) along with their associated:
  • email_assets      (1-2 per journey)
  • journey_activities (EMAIL type, linked to the email assets)
  • journey_entry_sources (schedule_start_time in the future)

Variety:
  • entry_type: EmailAudience (4), AutomationAudience (3), Schedule (1)
  • target_audience: Enrolled Undergrad, Inquired Graduate, Continuing Undergrad,
                     Applied Undergrad, Recent Alumni
  • business_unit: UC, GC, OL, MIL, INTL
  • departments: SFS, Admissions, Registrar, Career, Advising
  • schedule frequencies: Weekly, Monthly, Once, Daily

Run:
  python 08_seed_draft_journeys.py
"""

import os
import uuid
import random
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

UNIV        = "Avalon University"
UNIV_DOMAIN = "avalon.edu"
UNIV_URL    = "https://www.avalon.edu"

random.seed(2026_08)

# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())

def created_recently() -> datetime:
    """A realistic created/modified timestamp in early 2026."""
    d = date(2026, random.randint(1, 3), random.randint(1, 25))
    return datetime(d.year, d.month, d.day, random.randint(8, 17), random.randint(0, 59))

def staff_name() -> str:
    names = [
        "Diana Ferraro", "Marcus Webb", "Priya Chandran", "James Okoro",
        "Leah Stanton", "Carlos Mendez", "Naomi Huang", "Patrick Flynn",
        "Sophia Decker", "Raymond Torres",
    ]
    return random.choice(names)

def staff_email(name: str) -> str:
    return name.lower().replace(" ", ".") + f"@{UNIV_DOMAIN}"


# ─────────────────────────────────────────────────────────────────────────────
# Data definitions
# ─────────────────────────────────────────────────────────────────────────────

# Each email asset dict maps to the email_assets INSERT column list.
EMAIL_ASSETS = [

    # ── J1 ── Scholarship Renewal (UC / SFS / Enrolled Undergrad)
    {
        "asset_id":    "EA-DRAFT-10001",
        "legacy_id":   "LEG-91001",
        "unique_id":   "20260326_410001",
        "business_unit": "UC",
        "name":        "EM-UC-SFS-Scholarship-Renewal-Reminder",
        "subject_line": "Your Scholarship Renewal Application Is Now Open",
        "pre_header":  "Submit your renewal before the June 1 deadline to keep your award",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/SFS",
        "department_code": "SFS",
        "target_audience": "Enrolled Undergrad",
        "sender_address":  f"sfs@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Student Financial Services",
        "copy_found": (
            "Dear {first_name}, your Avalon University merit scholarship is up for renewal "
            "for the 2026-27 academic year. To maintain your award you must submit the "
            "scholarship renewal application by June 1, 2026. Log into the Student Portal, "
            "navigate to Financial Aid > Scholarships, and complete the renewal form. You "
            "will need to provide a brief statement of continued academic progress and confirm "
            "you meet the minimum 3.0 cumulative GPA requirement. If your GPA has fallen below "
            "3.0 this semester, contact your academic advisor to discuss options — an academic "
            "improvement plan may allow you to retain your award on a provisional basis. "
            "Students who miss the June 1 deadline will forfeit their scholarship for the "
            "upcoming year and must re-apply during the next open application cycle. Our SFS "
            "team is available Monday through Friday 8AM-5PM at sfs@avalon.edu or 800-555-0100."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @gpa set @gpa = AttributeValue('Cumulative_GPA__c') ]%%"
        ),
        "images":     "/images/student-cta-01.jpg",
        "urls_found": f"{UNIV_URL}/portal,{UNIV_URL}/financial-aid/scholarships,{UNIV_URL}/sfs",
        "emails_found": f"sfs@{UNIV_DOMAIN},advising@{UNIV_DOMAIN}",
        "content_blocks": "CB-30000,CB-30001",
    },

    # ── J2a ── PhD Recruitment Step 1 (GC / Admissions / Inquired Graduate)
    {
        "asset_id":    "EA-DRAFT-10002",
        "legacy_id":   "LEG-91002",
        "unique_id":   "20260326_410002",
        "business_unit": "GC",
        "name":        "EM-GC-ADM-PhD-Recruitment-Intro",
        "subject_line": "Advance Your Research Career — Apply to Avalon PhD Programs",
        "pre_header":  "Assistantships available — full tuition remission + monthly stipend",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/Admissions",
        "department_code": "Admissions",
        "target_audience": "Inquired Graduate",
        "sender_address":  f"graduate.admissions@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Graduate Admissions",
        "copy_found": (
            "Dear {first_name}, thank you for your interest in doctoral study at Avalon "
            "University. Our PhD programs are accepting applications for Fall 2026 entry, "
            "and I want to make sure you have the information you need to put together a "
            "competitive application. Avalon's doctoral programs span Education, Business, "
            "Health Sciences, Data Science, and the Humanities. Each program features a "
            "cohort model, dedicated faculty mentors, and a structured dissertation support "
            "track. Graduate assistantships provide full tuition remission and a monthly "
            "stipend starting at $1,800. The application deadline for assistantship "
            "consideration is May 15, 2026. To apply, visit graduate.avalon.edu/phd. "
            "I am happy to schedule a virtual call to walk you through the program options "
            "that best align with your research interests and career goals. Reply to this "
            "email or book a time at avalon.edu/grad-advising."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @prog set @prog = AttributeValue('Program_Interest__c') ]%%"
        ),
        "images":     "/images/grad-student-01.jpg",
        "urls_found": (
            f"{UNIV_URL}/graduate/phd,{UNIV_URL}/graduate/assistantships,"
            f"{UNIV_URL}/grad-advising"
        ),
        "emails_found": f"graduate.admissions@{UNIV_DOMAIN}",
        "content_blocks": "CB-30002,CB-30003",
    },

    # ── J2b ── PhD Recruitment Step 2 — deadline nudge
    {
        "asset_id":    "EA-DRAFT-10003",
        "legacy_id":   "LEG-91003",
        "unique_id":   "20260326_410003",
        "business_unit": "GC",
        "name":        "EM-GC-ADM-PhD-Recruitment-DeadlineNudge",
        "subject_line": "PhD Application Deadline Approaching — May 15 for Assistantships",
        "pre_header":  "Only a few weeks left to secure full funding for Fall 2026",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/Admissions",
        "department_code": "Admissions",
        "target_audience": "Inquired Graduate",
        "sender_address":  f"graduate.admissions@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Graduate Admissions",
        "copy_found": (
            "Dear {first_name}, the May 15, 2026 assistantship consideration deadline for "
            "Avalon University PhD programs is just weeks away. Submitting a complete "
            "application before this date gives you the strongest possible chance of being "
            "matched with a graduate assistantship that covers your full tuition and provides "
            "a monthly living stipend. If you have already started your application, log back "
            "in at graduate.avalon.edu/apply to confirm all required materials have been "
            "received. Applications missing transcripts, letters of recommendation, or a "
            "research statement are not considered for assistantship matching. If you have "
            "questions about program requirements or fit, your admissions counselor is "
            "available for a virtual appointment this week. We hope to see your completed "
            "application soon."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF ]%%"
        ),
        "images":     "/images/grad-student-01.jpg",
        "urls_found": f"{UNIV_URL}/graduate/apply,{UNIV_URL}/graduate/phd",
        "emails_found": f"graduate.admissions@{UNIV_DOMAIN}",
        "content_blocks": "CB-30002,CB-30004",
    },

    # ── J3 ── Summer Enrollment Reminder (OL / Registrar / Continuing Undergrad)
    {
        "asset_id":    "EA-DRAFT-10004",
        "legacy_id":   "LEG-91004",
        "unique_id":   "20260326_410004",
        "business_unit": "OL",
        "name":        "EM-OL-REG-Summer-2026-Enrollment-Open",
        "subject_line": "Summer 2026 Registration Is Now Open — Secure Your Courses",
        "pre_header":  "Online courses fill fast — register before seats are gone",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/Registrar",
        "department_code": "Registrar",
        "target_audience": "Continuing Undergrad",
        "sender_address":  f"registrar@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Registrar's Office",
        "copy_found": (
            "Dear {first_name}, summer 2026 course registration is now open for continuing "
            "online students. Summer is a great opportunity to accelerate your degree progress, "
            "make up prerequisite requirements, or explore an elective without the pressure of "
            "a full course load. Avalon's online summer sessions run June 8 through August 7, "
            "with eight-week and accelerated four-week format options available. To register, "
            "log into the Student Portal and navigate to Registration > Summer 2026. If you "
            "have any holds on your account — such as an unpaid balance or a missing "
            "immunization record — you will need to resolve them before registration opens for "
            "you. Holds are visible under Account Status in the portal. Summer tuition for "
            "online students is $350 per credit hour, and financial aid is available for "
            "students enrolled in six or more credit hours. Payment plans are also available "
            "for summer. Questions? Contact registrar@avalon.edu or call 800-555-0300."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @level set @level = AttributeValue('Student_Level__c') ]%%"
        ),
        "images":     "/images/student-cta-02.jpg",
        "urls_found": (
            f"{UNIV_URL}/portal,{UNIV_URL}/registration/summer-2026,"
            f"{UNIV_URL}/financial-aid"
        ),
        "emails_found": f"registrar@{UNIV_DOMAIN},sfs@{UNIV_DOMAIN}",
        "content_blocks": "CB-30000,CB-30001",
    },

    # ── J4 ── TA Authorization Renewal (MIL / SFS / Enrolled Undergrad — automation)
    {
        "asset_id":    "EA-DRAFT-10005",
        "legacy_id":   "LEG-91005",
        "unique_id":   "20260326_410005",
        "business_unit": "MIL",
        "name":        "EM-MIL-SFS-TA-Authorization-Renewal-26FA",
        "subject_line": "Action Required: Renew Your Tuition Assistance Authorization for Fall 2026",
        "pre_header":  "Submit your TA request before your enrollment deadline to avoid delays",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/SFS",
        "department_code": "SFS",
        "target_audience": "Enrolled Undergrad",
        "sender_address":  f"military@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Military Student Services",
        "copy_found": (
            "Dear {first_name}, as you prepare for Fall 2026 enrollment, now is the time to "
            "initiate your Tuition Assistance (TA) authorization through your branch education "
            "portal. TA authorization must be submitted and approved before the first day of "
            "each semester — late authorizations are not accepted and will result in your "
            "tuition balance being billed directly to you. If you are using Army TA, visit "
            "GoArmyEd.com. Air Force and Space Force students use the AFVEC portal. Navy and "
            "Marine Corps students log into MyNavyEducation.navy.mil. Coast Guard students "
            "visit the CGMA education portal. Once your TA is authorized, forward your "
            "approval document to military@avalon.edu so our team can apply your award to "
            "your student account before tuition is due. If your benefit has changed or you "
            "are transitioning between chapters, our Military Student Services advisors are "
            "available for one-on-one appointments Monday through Friday. Call 800-555-0200 "
            "or book online at military.avalon.edu."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @branch set @branch = AttributeValue('Military_Branch__c') ]%%"
        ),
        "images":     "/images/military-student-01.jpg",
        "urls_found": (
            f"{UNIV_URL}/military,{UNIV_URL}/military/ta-authorization,"
            "https://goarmyed.com"
        ),
        "emails_found": f"military@{UNIV_DOMAIN}",
        "content_blocks": "CB-30000,CB-30003",
    },

    # ── J5 ── Conditional Admit Nurture (INTL / Admissions / Applied Undergrad — automation)
    {
        "asset_id":    "EA-DRAFT-10006",
        "legacy_id":   "LEG-91006",
        "unique_id":   "20260326_410006",
        "business_unit": "INTL",
        "name":        "EM-INTL-ADM-Conditional-Admit-Nurture-Step1",
        "subject_line": "Your Path to Full Admission — Next Steps for Conditional Admits",
        "pre_header":  "Complete your English proficiency requirement before the July 1 deadline",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/Admissions",
        "department_code": "Admissions",
        "target_audience": "Applied Undergrad",
        "sender_address":  f"international.admissions@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} International Admissions",
        "copy_found": (
            "Dear {first_name}, congratulations on receiving a conditional admission offer "
            "from Avalon University for Fall 2026. A conditional offer means that your "
            "academic qualifications are strong, but one or more requirements must be "
            "completed before your admission becomes unconditional. The most common remaining "
            "requirement is English language proficiency. If you have not yet submitted "
            "official TOEFL or IELTS scores, please do so as soon as possible. Avalon's "
            "minimum requirements are a TOEFL iBT score of 80 or an IELTS overall band score "
            "of 6.5. Test scores must be sent directly from the testing organization and "
            "must be received by July 1, 2026 to remain eligible for Fall 2026 enrollment. "
            "Students who do not meet the English proficiency requirement by the deadline may "
            "be offered placement in Avalon's Intensive English Program (IEP) as a pathway "
            "to full enrollment. If your only remaining requirement is official final "
            "transcripts, those must be submitted within 30 days of your start date. Your "
            "admissions counselor has been assigned and will reach out separately to schedule "
            "a welcome call. In the meantime, please do not hesitate to contact our office "
            "at international.admissions@avalon.edu."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @country set @country = AttributeValue('Country_of_Origin__c') ]%%"
        ),
        "images":     "/images/intl-student-01.jpg",
        "urls_found": (
            f"{UNIV_URL}/international/admissions,{UNIV_URL}/international/english-program,"
            "https://ets.org/toefl"
        ),
        "emails_found": f"international.admissions@{UNIV_DOMAIN}",
        "content_blocks": "CB-30000,CB-30002",
    },

    # ── J6 ── Senior Career Launch (UC / Career / Continuing Undergrad — automation)
    {
        "asset_id":    "EA-DRAFT-10007",
        "legacy_id":   "LEG-91007",
        "unique_id":   "20260326_410007",
        "business_unit": "UC",
        "name":        "EM-UC-CAR-Senior-Career-Launch-26SP",
        "subject_line": "Your Career Launch Toolkit — Resources for Graduating Seniors",
        "pre_header":  "Internship hours, résumé reviews, and 150+ employer partners waiting for you",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/Career",
        "department_code": "Career",
        "target_audience": "Continuing Undergrad",
        "sender_address":  f"careers@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Career and Employment Center",
        "copy_found": (
            "Dear {first_name}, as a graduating senior your career launch is just months "
            "away, and the Avalon Career and Employment Center is ready to help you cross "
            "the finish line in the strongest possible position. This semester we are offering "
            "extended drop-in hours Monday through Friday 9AM to 5PM for résumé and cover "
            "letter reviews — no appointment needed. Our employer relations team has over 150 "
            "active recruiting partners looking for Avalon graduates right now, including "
            "regional health systems, national technology firms, financial services companies, "
            "and nonprofits. Log into the Avalon Career Portal at careers.avalon.edu to "
            "browse open positions, register for on-campus recruiting events, and book a "
            "one-on-one coaching session. The Spring Career Fair is scheduled for April 24, "
            "2026 — over 90 employers will be on campus and actively hiring. Bring printed "
            "résumés and business casual attire. We also host a Senior Send-Off series of "
            "workshops covering salary negotiation, professional networking, and first-90-days "
            "workplace strategies. Check the events calendar in the Career Portal for dates "
            "and registration. We are proud of your achievements and committed to helping you "
            "succeed in the next chapter."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @major set @major = AttributeValue('Program_Name__c') ]%%"
        ),
        "images":     "/images/campus-hero-01.jpg",
        "urls_found": (
            f"{UNIV_URL}/careers,{UNIV_URL}/careers/fair,"
            f"{UNIV_URL}/careers/portal"
        ),
        "emails_found": f"careers@{UNIV_DOMAIN}",
        "content_blocks": "CB-30001,CB-30004",
    },

    # ── J7 ── Alumni Re-Engagement (GC / Advising / Recent Alumni)
    {
        "asset_id":    "EA-DRAFT-10008",
        "legacy_id":   "LEG-91008",
        "unique_id":   "20260326_410008",
        "business_unit": "GC",
        "name":        "EM-GC-AV-Alumni-Graduate-ReEngagement",
        "subject_line": "Come Back to Avalon — Explore Graduate Program Options",
        "pre_header":  "As an Avalon alum you qualify for a 15% tuition discount on graduate programs",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/Advising",
        "department_code": "Advising",
        "target_audience": "Recent Alumni",
        "sender_address":  f"alumni@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Alumni Relations",
        "copy_found": (
            "Dear {first_name}, it has been a while since you walked across the stage at "
            "Avalon University, and we hope your career has been everything you worked so "
            "hard for. We are reaching out because many of our alumni are returning to "
            "Avalon to pursue graduate degrees — and as an Avalon alum, you qualify for a "
            "15% tuition discount on all master's degree programs. Our graduate programs "
            "are designed for working professionals, with evening, weekend, and fully online "
            "formats available. The most popular options among returning alumni include the "
            "MBA with concentrations in Healthcare Management and Data Analytics, the Master "
            "of Education for those moving into leadership roles in their organizations, and "
            "the MS in Data Science. Applications for Fall 2026 are open now. The process is "
            "streamlined for alumni — we already have your undergraduate transcript on file, "
            "so you only need to submit your personal statement and two professional "
            "references. Start your application at graduate.avalon.edu/alumni-return or "
            "reach out to an alumni admissions advisor at alumni@avalon.edu."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @gradyear set @gradyear = AttributeValue('Graduation_Year__c') ]%%"
        ),
        "images":     "/images/alumni-event-01.jpg",
        "urls_found": (
            f"{UNIV_URL}/graduate/alumni-return,{UNIV_URL}/graduate,"
            f"{UNIV_URL}/alumni"
        ),
        "emails_found": f"alumni@{UNIV_DOMAIN},graduate.admissions@{UNIV_DOMAIN}",
        "content_blocks": "CB-30002,CB-30003",
    },

    # ── J8 ── Financial Aid Re-Packaging (OL / SFS / Applied Undergrad)
    {
        "asset_id":    "EA-DRAFT-10009",
        "legacy_id":   "LEG-91009",
        "unique_id":   "20260326_410009",
        "business_unit": "OL",
        "name":        "EM-OL-SFS-FinAid-Repackaging-26FA",
        "subject_line": "Your Updated Financial Aid Package for Fall 2026 Is Ready",
        "pre_header":  "Your aid offer has been revised — review it before the June 15 deadline",
        "asset_type_name": "templatebasedemail",
        "asset_type_id":   "207",
        "folder":      "Folder/SFS",
        "department_code": "SFS",
        "target_audience": "Applied Undergrad",
        "sender_address":  f"sfs@{UNIV_DOMAIN}",
        "sender_name":     f"{UNIV} Student Financial Services",
        "copy_found": (
            "Dear {first_name}, your financial aid offer for Fall 2026 has been updated "
            "based on recent changes to your FAFSA or enrollment information. Please log "
            "into the Student Portal and navigate to Financial Aid > My Awards to review "
            "your revised package. Your updated offer may include changes to grant amounts, "
            "scholarship eligibility, or loan options based on your expected family "
            "contribution, enrollment status, or academic standing. You must accept or "
            "decline each component of your award by June 15, 2026. Awards not accepted by "
            "this deadline will be released to other eligible students. If you have questions "
            "about your award or believe there has been an error, please contact our SFS "
            "team directly at sfs@avalon.edu or call 800-555-0100. We are available Monday "
            "through Friday 8AM to 6PM and Saturdays 10AM to 2PM during peak enrollment "
            "season. If your financial circumstances have changed significantly since you "
            "submitted your FAFSA, you may be eligible to request a professional judgment "
            "review — ask your SFS counselor for details."
        ),
        "ampscript": (
            "%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            "IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            "var @efc set @efc = AttributeValue('Expected_Family_Contribution__c') ]%%"
        ),
        "images":     "/images/financial-doc-01.jpg",
        "urls_found": (
            f"{UNIV_URL}/portal,{UNIV_URL}/financial-aid/awards,"
            f"{UNIV_URL}/financial-aid/professional-judgment"
        ),
        "emails_found": f"sfs@{UNIV_DOMAIN}",
        "content_blocks": "CB-30000,CB-30001",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Journey definitions
# Each tuple: (journey_name, bu, target_audience, department, academic_term,
#              target_audience_detail, entry_type, schedule_frequency,
#              schedule_start_date, schedule_end_date, email_asset_ids [list])
# ─────────────────────────────────────────────────────────────────────────────

JOURNEY_DEFS = [
    # J1 — Scholarship Renewal (EmailAudience / Weekly / UC)
    {
        "name":       "JB-UC-SFS-Scholarship-Renewal-26SU",
        "bu":         "UC",
        "audience":   "Campus",
        "dept":       "SFS",
        "term":       "26SU",
        "ta_detail":  "Enrolled Undergrad",
        "entry_type": "EmailAudience",
        "frequency":  "Weekly",
        "start":      date(2026, 4, 7),
        "end":        date(2026, 6, 1),
        "email_ids":  ["EA-DRAFT-10001"],
    },

    # J2 — PhD Recruitment Nurture (EmailAudience / Monthly / GC)
    {
        "name":       "JB-GC-ADM-PhD-Recruitment-26FA",
        "bu":         "GC",
        "audience":   "Graduate",
        "dept":       "Admissions",
        "term":       "26FA",
        "ta_detail":  "Inquired Graduate",
        "entry_type": "EmailAudience",
        "frequency":  "Monthly",
        "start":      date(2026, 4, 15),
        "end":        date(2026, 5, 15),
        "email_ids":  ["EA-DRAFT-10002", "EA-DRAFT-10003"],
    },

    # J3 — Summer Enrollment Reminder (EmailAudience / Once / OL)
    {
        "name":       "JB-OL-REG-Summer-Enrollment-Reminder-26SU",
        "bu":         "OL",
        "audience":   "Enrolled",
        "dept":       "Registrar",
        "term":       "26SU",
        "ta_detail":  "Continuing Undergrad",
        "entry_type": "EmailAudience",
        "frequency":  "Once",
        "start":      date(2026, 4, 20),
        "end":        date(2026, 5, 1),
        "email_ids":  ["EA-DRAFT-10004"],
    },

    # J4 — TA Authorization Renewal (AutomationAudience / Monthly / MIL)
    {
        "name":       "JB-MIL-SFS-TA-Authorization-Renewal-26FA",
        "bu":         "MIL",
        "audience":   "Military",
        "dept":       "SFS",
        "term":       "26FA",
        "ta_detail":  "Enrolled Undergrad",
        "entry_type": "AutomationAudience",
        "frequency":  "Monthly",
        "start":      date(2026, 5, 1),
        "end":        date(2026, 8, 1),
        "email_ids":  ["EA-DRAFT-10005"],
    },

    # J5 — Conditional Admit Nurture (AutomationAudience / Weekly / INTL)
    {
        "name":       "JB-INTL-ADM-Conditional-Admit-Nurture-26FA",
        "bu":         "INTL",
        "audience":   "International",
        "dept":       "Admissions",
        "term":       "26FA",
        "ta_detail":  "Applied Undergrad",
        "entry_type": "AutomationAudience",
        "frequency":  "Weekly",
        "start":      date(2026, 4, 28),
        "end":        date(2026, 7, 1),
        "email_ids":  ["EA-DRAFT-10006"],
    },

    # J6 — Senior Career Launch (AutomationAudience / Weekly / UC)
    {
        "name":       "JB-UC-CAR-Senior-Career-Launch-26SP",
        "bu":         "UC",
        "audience":   "Senior",
        "dept":       "Career",
        "term":       "26SP",
        "ta_detail":  "Continuing Undergrad",
        "entry_type": "AutomationAudience",
        "frequency":  "Weekly",
        "start":      date(2026, 4, 14),
        "end":        date(2026, 5, 16),
        "email_ids":  ["EA-DRAFT-10007"],
    },

    # J7 — Alumni Re-Engagement (EmailAudience / Monthly / GC)
    {
        "name":       "JB-GC-AV-Alumni-Graduate-ReEngagement-26FA",
        "bu":         "GC",
        "audience":   "Alumni",
        "dept":       "Advising",
        "term":       "26FA",
        "ta_detail":  "Recent Alumni",
        "entry_type": "EmailAudience",
        "frequency":  "Monthly",
        "start":      date(2026, 6, 1),
        "end":        date(2026, 9, 1),
        "email_ids":  ["EA-DRAFT-10008"],
    },

    # J8 — Financial Aid Re-Packaging (Schedule / Daily burst / OL)
    {
        "name":       "JB-OL-SFS-FinAid-Repackaging-26FA",
        "bu":         "OL",
        "audience":   "Inquiry",
        "dept":       "SFS",
        "term":       "26FA",
        "ta_detail":  "Applied Undergrad",
        "entry_type": "Schedule",
        "frequency":  "Daily",
        "start":      date(2026, 5, 12),
        "end":        date(2026, 6, 15),
        "email_ids":  ["EA-DRAFT-10009"],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# seed functions
# ─────────────────────────────────────────────────────────────────────────────

def seed_email_assets(cur):
    print("  Inserting email_assets...")
    rows = []
    for ea in EMAIL_ASSETS:
        creator  = staff_name()
        modifier = staff_name()
        created  = created_recently()
        modified = created + timedelta(days=random.randint(1, 30))
        rows.append((
            ea["asset_id"],
            ea["legacy_id"],
            ea["unique_id"],
            ea["business_unit"],
            ea["name"],
            ea["subject_line"],
            ea["pre_header"],
            ea["asset_type_name"],
            ea["asset_type_id"],
            ea["folder"],
            ea["department_code"],
            ea["target_audience"],
            ea["sender_address"],
            ea["sender_name"],
            ea["copy_found"],
            ea["ampscript"],
            ea["images"],
            ea["urls_found"],
            ea["emails_found"],
            ea["content_blocks"],
            creator,
            staff_email(creator),
            modifier,
            staff_email(modifier),
            created,
            modified,
            new_id(),   # object_id
        ))
    execute_values(cur, """
        INSERT INTO email_assets
            (asset_id, legacy_id, unique_id, business_unit, name,
             subject_line, pre_header, asset_type_name, asset_type_id,
             folder, department_code, target_audience,
             sender_address, sender_name, copy_found, ampscript,
             images, urls_found, emails_found, content_blocks,
             created_by_name, created_by_email,
             last_modified_by_name, last_modified_by_email,
             created_time, last_modified_date, object_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, rows)
    print(f"    {len(rows)} email_assets rows upserted")


def seed_journeys_and_related(cur):
    """Insert journeys, journey_entry_sources, and journey_activities."""
    print("  Inserting journeys, journey_entry_sources, journey_activities...")
    j_rows   = []
    jes_rows = []
    ja_rows  = []

    for jdef in JOURNEY_DEFS:
        jid   = new_id()
        jkey  = new_id()
        evdef = new_id()
        created  = created_recently()
        modified = created + timedelta(days=random.randint(1, 20))

        # ── journey row ──────────────────────────────────────────────────────
        j_rows.append((
            jid,
            jkey,
            jdef["name"],
            f"Journey for {jdef['ta_detail']} — {jdef['dept']} department",
            jdef["bu"],
            "Draft",
            1,                              # version
            1.0,                            # workflow_api_version
            "SingleEntryAcrossAllVersions",
            evdef,
            modified,
            created,
            jdef["audience"],
            jdef["dept"],
            jdef["term"],
            jdef["ta_detail"],
        ))

        # ── journey entry source ─────────────────────────────────────────────
        start_dt = datetime(
            jdef["start"].year,
            jdef["start"].month,
            jdef["start"].day,
            8, 0,
        )
        end_dt = datetime(
            jdef["end"].year,
            jdef["end"].month,
            jdef["end"].day,
            23, 59,
        )
        jes_rows.append((
            new_id(),           # entry_source_id
            jid,
            jdef["name"],
            jdef["bu"],
            jdef["entry_type"],
            f"JB-EV-{jdef['name'][:40]}",
            evdef,
            new_id(),           # data_extension_id
            f"DE-{jdef['name'][:50]}",
            None,               # automation_id — NULL (draft; not yet linked)
            jdef["ta_detail"],
            "Production",
            jdef["frequency"],
            start_dt,
            end_dt,
            random.randint(1, 6),
            staff_name(),
            staff_name(),
        ))

        # ── journey activities — one per email asset ─────────────────────────
        for step_idx, email_asset_id in enumerate(jdef["email_ids"], start=1):
            # look up the email asset metadata
            ea = next(e for e in EMAIL_ASSETS if e["asset_id"] == email_asset_id)
            act_modified = modified + timedelta(days=random.randint(0, 10))
            ja_rows.append((
                new_id(),               # activity_id
                jid,
                jdef["name"],
                new_id(),               # activity_key
                jdef["bu"],
                f"EMAILV2-{step_idx}",
                f"Email Step {step_idx}: {ea['name'][:50]}",
                "EMAIL",
                email_asset_id,
                ea["name"],
                ea["subject_line"],
                ea["pre_header"],
                "Draft",                # send_status mirrors journey status
                new_id(),               # send_key
                new_id(),               # triggered_send_id
                True,                   # salesforce_tracking
                True,                   # send_logging
                True,                   # click_tracking
                f"AU-{jdef['name'][:35]}-step{step_idx}",
                jdef["ta_detail"],
                staff_name(),
                act_modified,
            ))

    # ── bulk inserts ─────────────────────────────────────────────────────────
    execute_values(cur, """
        INSERT INTO journeys
            (journey_id, journey_key, journey_name, description,
             business_unit, status, version, workflow_api_version,
             entry_mode, event_definition_id,
             last_modified_date, created_date,
             target_audience, department, academic_term,
             target_audience_detail)
        VALUES %s ON CONFLICT DO NOTHING
    """, j_rows)
    print(f"    {len(j_rows)} journey rows upserted")

    execute_values(cur, """
        INSERT INTO journey_entry_sources
            (entry_source_id, journey_id, journey_name, business_unit,
             entry_type, event_definition_key,
             event_definition_id, data_extension_id, data_extension_name,
             automation_id, target_audience, mode, schedule_frequency,
             schedule_start_time, schedule_end_time, schedule_occurrences,
             created_by, last_modified_by)
        VALUES %s ON CONFLICT DO NOTHING
    """, jes_rows)
    print(f"    {len(jes_rows)} journey_entry_source rows upserted")

    execute_values(cur, """
        INSERT INTO journey_activities
            (activity_id, journey_id, journey_name, activity_key, business_unit,
             activity_name, activity_description, activity_type,
             email_id, email_name, email_subject, email_pre_header,
             send_status, send_key, triggered_send_id,
             salesforce_tracking, send_logging, click_tracking,
             ga_campaign_name, target_audience,
             last_modified_by, last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, ja_rows)
    print(f"    {len(ja_rows)} journey_activity rows upserted")


# ─────────────────────────────────────────────────────────────────────────────
# verification
# ─────────────────────────────────────────────────────────────────────────────

def verify(conn):
    print("\n── Verification ──────────────────────────────────────────────────")
    checks = [
        ("Draft journeys inserted",
         "SELECT COUNT(*) FROM journeys "
         "WHERE journey_name LIKE 'JB-%' AND status = 'Draft' "
         "  AND created_date >= '2026-01-01'"),

        ("Draft journey names",
         "SELECT journey_name, business_unit, target_audience_detail "
         "FROM journeys WHERE status = 'Draft' AND created_date >= '2026-01-01' "
         "ORDER BY journey_name"),

        ("Future entry sources (start > 2026-03-26)",
         "SELECT COUNT(*) FROM journey_entry_sources jes "
         "JOIN journeys j ON j.journey_id = jes.journey_id "
         "WHERE j.status = 'Draft' AND jes.schedule_start_time > '2026-03-26'"),

        ("Entry type breakdown",
         "SELECT jes.entry_type, COUNT(*) FROM journey_entry_sources jes "
         "JOIN journeys j ON j.journey_id = jes.journey_id "
         "WHERE j.status = 'Draft' AND jes.schedule_start_time > '2026-03-26' "
         "GROUP BY jes.entry_type ORDER BY jes.entry_type"),

        ("Journey activities for new drafts",
         "SELECT COUNT(*) FROM journey_activities ja "
         "JOIN journeys j ON j.journey_id = ja.journey_id "
         "WHERE j.status = 'Draft' AND j.created_date >= '2026-01-01'"),

        ("Email assets for new drafts",
         "SELECT COUNT(*) FROM email_assets WHERE asset_id LIKE 'EA-DRAFT-%'"),

        ("Schedule frequency breakdown",
         "SELECT jes.schedule_frequency, COUNT(*) "
         "FROM journey_entry_sources jes "
         "JOIN journeys j ON j.journey_id = jes.journey_id "
         "WHERE j.status = 'Draft' AND j.created_date >= '2026-01-01' "
         "GROUP BY jes.schedule_frequency ORDER BY jes.schedule_frequency"),
    ]
    cur = conn.cursor()
    for label, sql in checks:
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 1 and len(rows[0]) == 1:
            print(f"  {label:<55}  {rows[0][0]}")
        else:
            print(f"  {label}:")
            for row in rows:
                print(f"    {'  '.join(str(v) for v in row)}")
    cur.close()


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        raise SystemExit(1)

    conn = psycopg2.connect(DATABASE_URL)
    cur  = conn.cursor()

    print(f"\n🚀  Seeding 8 scheduled Draft journeys (schedule_start > 2026-03-26)\n")

    print("── Step 1/2  Email assets ────────────────────────────────────────")
    seed_email_assets(cur)
    conn.commit()

    print("── Step 2/2  Journeys + entry sources + activities ───────────────")
    seed_journeys_and_related(cur)
    conn.commit()

    cur.close()

    verify(conn)
    conn.close()
    print("\n✅  Done — 8 Draft journeys with future schedules inserted.")


if __name__ == "__main__":
    main()
