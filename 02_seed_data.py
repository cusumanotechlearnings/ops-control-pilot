"""
02_seed_data.py  —  Avalon University Marketing Ops AI
Full replacement seed script incorporating all feedback:
  • Fictional university: Avalon University (avalon.edu)
  • target_audience on all relevant tables
  • Academic terms split by population (UG / GR / PhD)
  • automation_activities populated
  • More automations with weekly / monthly / one-time schedules
  • content_block_assets: substantive copy, ampscript, images, urls
  • email_assets: substantive copy, ampscript, images, content_blocks
  • image_assets: image_description field
  • landing_page_assets: substantive copy, more rows, folder variation
  • sql_queries: SFMC bracket-notation audience queries
  • voc_responses: new table, contextual, equal thirds sentiment
  • All SNHU references removed

Run:
  pip install psycopg2-binary faker python-dotenv
  python 02_seed_data.py
"""

import os, random, uuid
from datetime import datetime, timedelta, date
from faker import Faker
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()
fake = Faker()
random.seed(42)
Faker.seed(42)

DATABASE_URL = os.getenv("DATABASE_URL")

# ── constants ────────────────────────────────────────────────
UNIV       = "Avalon University"
UNIV_SHORT = "Avalon"
UNIV_ABBR  = "AU"
UNIV_DOMAIN = "avalon.edu"
UNIV_URL    = "https://www.avalon.edu"

BUS_UNITS = ["UC", "GC", "OL", "MIL", "INTL"]

TARGET_AUDIENCES = [
    "Enrolled Undergrad", "First Term Grad", "Applied Undergrad",
    "Recent Alumni", "Inquired Graduate", "Enrolled Graduate",
    "Applied Graduate", "Inquired Undergrad", "Continuing Undergrad",
    "Stopped Out", "ClosedLost", "Lapsed Student",
]

DEPARTMENTS = ["SFS", "Advising", "Admissions", "FA",
               "Registrar", "Housing", "Career", "Events"]

SEGMENTS = ["Military", "International", "Freshman", "Senior",
            "Graduate", "Campus", "Transfer", "Alumni", "Inquiry"]

# ── helper functions ─────────────────────────────────────────
def rand_date(y0=2023, y1=2025):
    s = date(y0, 1, 1); e = date(y1, 12, 31)
    return s + timedelta(days=random.randint(0, (e-s).days))

def rand_ts(y0=2023, y1=2025):
    d = rand_date(y0, y1)
    return datetime(d.year, d.month, d.day,
                    random.randint(6,18), random.randint(0,59))

def rand_rate(base, spread=0.06):
    return round(max(0.001, min(0.999,
           base + random.gauss(0, spread))), 6)

def staff_name(): return fake.name()
def staff_email(name=None):
    n = (name or fake.name()).lower().replace(" ",".")
    return f"{n}@{UNIV_DOMAIN}"

# ── ACADEMIC TERMS ───────────────────────────────────────────
TERM_DATA = [
    # (term_code, term_name, start, end, acad_year, season, population, notes)
    ("23FA","Fall 2023","2023-09-05","2023-12-20","FY2024","Fall","Undergraduate","Standard 16-week semester"),
    ("23FA","Fall 2023","2023-09-12","2023-12-15","FY2024","Fall","Graduate","Accelerated 14-week format"),
    ("23FA","Fall 2023","2023-09-19","2023-12-08","FY2024","Fall","PhD / Doctoral","Research-focused, flexible pacing"),
    ("24SP","Spring 2024","2024-01-16","2024-05-10","FY2024","Spring","Undergraduate","Standard 16-week semester"),
    ("24SP","Spring 2024","2024-01-23","2024-05-03","FY2024","Spring","Graduate","Accelerated 14-week format"),
    ("24SP","Spring 2024","2024-01-30","2024-04-26","FY2024","Spring","PhD / Doctoral","Research-focused, flexible pacing"),
    ("24SU","Summer 2024","2024-06-03","2024-08-09","FY2024","Summer","Undergraduate","Condensed 10-week session"),
    ("24SU","Summer 2024","2024-06-10","2024-08-02","FY2024","Summer","Graduate","Condensed 8-week session"),
    ("24FA","Fall 2024","2024-09-04","2024-12-18","FY2025","Fall","Undergraduate","Standard 16-week semester"),
    ("24FA","Fall 2024","2024-09-11","2024-12-13","FY2025","Fall","Graduate","Accelerated 14-week format"),
    ("24FA","Fall 2024","2024-09-18","2024-12-06","FY2025","Fall","PhD / Doctoral","Research-focused, flexible pacing"),
    ("25SP","Spring 2025","2025-01-14","2025-05-09","FY2025","Spring","Undergraduate","Standard 16-week semester"),
    ("25SP","Spring 2025","2025-01-21","2025-05-02","FY2025","Spring","Graduate","Accelerated 14-week format"),
    ("25SP","Spring 2025","2025-01-28","2025-04-25","FY2025","Spring","PhD / Doctoral","Research-focused, flexible pacing"),
    ("25FA","Fall 2025","2025-09-03","2025-12-17","FY2026","Fall","Undergraduate","Standard 16-week semester"),
    ("25FA","Fall 2025","2025-09-10","2025-12-12","FY2026","Fall","Graduate","Accelerated 14-week format"),
    ("25FA","Fall 2025","2025-09-17","2025-12-05","FY2026","Fall","PhD / Doctoral","Research-focused, flexible pacing"),
]

# ── EMAIL TEMPLATES ──────────────────────────────────────────
EMAIL_TEMPLATES = [
    ("EM-SFS-UC-FAFSA-Available-Incoming",
     "SFS","UC","Applied Undergrad",
     "The 2025-26 FAFSA is Now Available",
     "Complete your FAFSA today to ensure financial aid eligibility",
     """Dear {first_name}, congratulations on your acceptance to Avalon University! To be considered for federal financial aid for the upcoming academic year, you will need to complete the 2025-26 Free Application for Federal Student Aid (FAFSA) at studentaid.gov. Avalon University's federal school code is 004821. The FAFSA uses your 2023 tax information and typically takes about 30 minutes to complete. We strongly encourage you to submit your application as soon as possible to maximize your financial aid eligibility. Students who complete the FAFSA early receive their financial aid offers first, which helps you plan for your first semester. If you have questions about the process or need help interpreting your Student Aid Report, our Student Financial Services team is available Monday through Friday from 8am to 5pm. You can reach us by phone at 800-555-0100 or by email at financialaid@avalon.edu. We look forward to helping you make your Avalon education affordable."""),

    ("EM-SFS-UC-Federal_Work_Study",
     "SFS","UC","Enrolled Undergrad",
     "You've Been Offered Federal Work-Study — Now What?",
     "Start earning and building your campus community",
     """Dear {first_name}, great news — you have been offered Federal Work-Study as part of your financial aid package for the current academic year. Federal Work-Study is a federally funded program that provides part-time employment opportunities to help you cover educational expenses while gaining valuable professional experience. You can work on campus in departments like the library, athletics, student services, or academic tutoring centers, or off campus with approved community service partners. To get started, visit the Student Employment portal on the Avalon University website and browse available positions. New employees must complete a federal I-9 form and provide original identity documents before their first shift. If you have previously worked at Avalon, please log into Workday and search for current openings. Work-Study positions typically pay between $12 and $16 per hour and offer flexible scheduling around your class commitments. For questions about eligibility, award amounts, or finding a position, contact the Student Employment Office at studentjobs@avalon.edu or stop by the Career and Employment Center in Donovan Hall, Room 102."""),

    ("EM-FA-AWD-CFP-MIL-CollegeFinancingPlan",
     "FA","MIL","Enrolled Undergrad",
     "Important: Your College Financing Plan Is Ready",
     "Review your personalized cost and aid summary",
     """Dear {first_name}, your College Financing Plan is now available in your Avalon University student portal. As an identified beneficiary of military educational benefits — including VA Chapters 30, 31, 33, or 35, or Tuition Assistance through the Army, Navy, Marines, Air Force, Space Force, or Coast Guard — you are required by federal law to receive this standardized disclosure document. The College Financing Plan summarizes your estimated cost of attendance, the financial aid and military benefits you have been awarded, and the remaining balance you may need to cover out of pocket or through loans. We encourage you to review this document carefully before finalizing your enrollment decision. If you have questions about your VA certification, TA authorization, or Yellow Ribbon eligibility, please contact our Military Student Services office at military@avalon.edu or call 800-555-0200. Our dedicated military advisors are available Monday through Friday and can assist you with benefits paperwork, enrollment certification, and connecting you with the Avalon veteran student community."""),

    ("EM-UC-AV-Add_Drop_Deadline",
     "Advising","UC","Enrolled Undergrad",
     "Reminder: Add/Drop Deadline Is This Friday",
     "Make any schedule changes before the deadline",
     """Dear {first_name}, this is a friendly reminder that the add/drop period for the current semester ends this Friday at 5:00 PM Eastern Time. After this deadline, you will not be able to add new courses or drop courses without academic and financial penalties. If you are considering any changes to your schedule, please log into the student portal now and make your adjustments. Adding a course after the deadline requires instructor and department approval and is rarely granted. Dropping a course after the deadline will result in a W (Withdrawal) appearing on your academic transcript and may affect your financial aid eligibility if you fall below full-time status. If you are unsure whether a schedule change is right for you, we encourage you to speak with your academic advisor before the deadline. You can schedule a same-day advising appointment through the Advising portal or by calling 800-555-0300. Your advisor can review your degree progress, discuss the implications of any changes, and help you make the best decision for your academic goals."""),

    ("EM-UC-AV-Final_Grades_Available",
     "Advising","UC","Continuing Undergrad",
     "Your Final Grades Are Now Posted",
     "Review your grades and plan for next semester",
     """Dear {first_name}, your final grades for the current semester are now available in your Avalon University student portal under the My Courses section. We encourage you to review your grades carefully and take note of a few important items as you plan for the upcoming semester. To remain in good academic standing, you must maintain a cumulative GPA of 2.0 or above. Students who fall below this threshold will be reviewed by the Scholastic Standing Committee and may be placed on academic probation. Please review the Academic Catalog to ensure you have completed all prerequisites for your planned spring courses. If any of your grades are lower than expected, we encourage you to connect with your professor during office hours or reach out to Academic Support Services for tutoring and study skills resources. Registration for the upcoming semester is currently open, and we encourage you to complete your registration as soon as possible to secure your preferred courses and time slots. Your academic advisor is available to help you plan a schedule that keeps you on track toward graduation."""),

    ("EM-GC-AV-Commencement-Announcement",
     "Advising","GC","Enrolled Graduate",
     "Commencement Ceremony Details — You're Almost There",
     "Everything you need to know about your graduation ceremony",
     """Dear {first_name}, congratulations — you are approaching the finish line of your graduate degree at Avalon University, and we could not be more proud of your dedication and hard work. Commencement ceremonies for graduate degree candidates will be held on Saturday, May 17th, 2025, at the Avalon University Events Center. The ceremony begins at 10:00 AM, and we ask that all candidates arrive by 8:30 AM for line-up and regalia distribution. Each graduate may invite up to four guests, and complimentary tickets are available through your student portal beginning April 1st. Additional tickets may be available based on venue capacity and will be distributed on a first-come, first-served basis starting April 15th. Academic regalia can be ordered through the Avalon University Bookstore online store or picked up in person at the campus bookstore through May 9th. A graduate breakfast and photo opportunity will be held the morning of the ceremony. For students completing degree requirements in summer 2025, you are welcome to participate in the May ceremony with advance approval from the Graduate School office. Please contact graduation@avalon.edu with any questions."""),

    ("EM-OL-ADM-Application-Received",
     "Admissions","OL","Inquired Undergrad",
     "We Received Your Application — What Happens Next",
     "Your Avalon University application is under review",
     """Dear {first_name}, thank you for applying to Avalon University's online degree programs. We are excited to review your application and learn more about your goals and background. Your application has been received and assigned to an admissions counselor who will be your primary point of contact throughout the review process. You can expect to hear from your counselor within 3 to 5 business days. In the meantime, you can track your application status in real time by logging into the Avalon Admissions Portal at apply.avalon.edu. If we need additional documents — such as official transcripts, letters of recommendation, or a personal statement — your counselor will reach out directly. Avalon University evaluates applicants holistically, considering academic history, professional experience, and personal motivation. There is no minimum GPA requirement for most online programs, and transfer credits from accredited institutions are accepted on a course-by-course basis. If you have questions about specific program requirements, scholarship opportunities, or the enrollment process, please do not hesitate to reach out to your admissions counselor or visit our website at avalon.edu/online."""),

    ("EM-MIL-ADM-TA-Benefits-Guide",
     "Admissions","MIL","Applied Undergrad",
     "Your Guide to Tuition Assistance at Avalon University",
     "Everything you need to know about using your TA benefit",
     """Dear {first_name}, thank you for your interest in Avalon University and for your service to our country. We want to make sure you have all the information you need to maximize your military Tuition Assistance (TA) benefit at Avalon. TA covers up to $250 per credit hour and up to $4,500 per fiscal year for active duty service members across all branches. Avalon University is approved for TA by all branches of the military and participates in the Department of Defense Voluntary Education Partnership. To use your TA benefit, you will need to obtain TA authorization through your branch's education portal (GoArmyEd, Navy College, Air Force Virtual Education Center, etc.) before the start of each course. Our Military Student Services team can walk you through the authorization process step by step. In addition to TA, Avalon offers Yellow Ribbon Program participation for post-9/11 GI Bill users, meaning we cover tuition costs that exceed the GI Bill cap at no cost to you. We also offer a dedicated military student orientation, priority registration, and a peer mentorship program connecting you with veteran students who have successfully navigated the same process. Contact our military admissions team at military@avalon.edu or call 800-555-0200."""),

    ("EM-INTL-ADM-Visa-Requirements",
     "Admissions","INTL","Applied Undergrad",
     "Important: Visa and Immigration Information for Incoming Students",
     "Required steps before your arrival at Avalon University",
     """Dear {first_name}, congratulations on your acceptance to Avalon University. As an international student, there are several important steps you must complete before your arrival on campus, and we want to make sure you have all the information you need to navigate this process smoothly. First, you will need to obtain your Form I-20 from Avalon University's Office of International Student Services. To receive your I-20, you must submit proof of financial support demonstrating that you can cover your first year of tuition and living expenses. Once you receive your I-20, you can pay the SEVIS fee and schedule your visa interview at the nearest U.S. Embassy or Consulate. We strongly recommend scheduling your interview as early as possible, as wait times can be several weeks in some countries. Upon arrival, you must report to the International Student Services office within 10 days of your program start date to complete your SEVIS registration. Avalon University offers a comprehensive international student orientation the week before classes begin, covering academic expectations, campus resources, health insurance requirements, and social programming. Our international student advisors are available year-round to assist with visa renewals, OPT and CPT authorization, and any immigration questions that arise during your studies."""),

    ("EM-UC-REG-Registration-Reminder",
     "Registrar","UC","Continuing Undergrad",
     "Registration for Spring 2025 Opens Next Week",
     "Your registration window and priority date inside",
     """Dear {first_name}, spring 2025 registration is opening soon, and your individual registration window is determined by your earned credit hours. Senior students (90+ credits) open first, followed by juniors, sophomores, and freshmen. Your specific registration date and time are posted in your student portal under the Registration section. We encourage you to prepare in advance by meeting with your academic advisor to review your degree audit, identify any remaining requirements, and plan your course selection. Advisor appointments are available online through the Advising portal. Before you can register, make sure you have resolved any holds on your account — common holds include unpaid balances, missing immunization records, and incomplete orientation requirements. You can view and address your holds in the student portal under Account Status. Popular courses fill quickly, especially those that satisfy general education or major requirements, so we encourage you to register as early as your window allows and to identify backup options for each course. If you have questions about course selection, degree requirements, or registration procedures, your academic advisor is your best resource. Walk-in advising hours are available Monday through Thursday from 1:00 PM to 4:00 PM in Whitmore Hall."""),

    ("EM-GC-ADM-Graduate-Program-Info",
     "Admissions","GC","Inquired Graduate",
     "Explore Graduate Programs at Avalon University",
     "Find the right program for your career goals",
     """Dear {first_name}, thank you for your interest in graduate education at Avalon University. We offer over 40 master's degree and doctoral programs across business, education, health sciences, technology, and the humanities — all designed to advance your career while accommodating your professional and personal commitments. Our graduate programs feature small cohort sizes, faculty who are active practitioners in their fields, and flexible scheduling options including evening, weekend, and fully online formats. Many students complete their master's degrees while working full time. Graduate assistantships and fellowships are available for qualified applicants in most doctoral programs, providing tuition remission and a stipend in exchange for research or teaching responsibilities. The application process is straightforward: submit your application online, provide official transcripts from all previous institutions, and include a personal statement describing your professional goals and interest in your chosen program. Most programs do not require the GRE, though some doctoral programs may request it. An admissions counselor will review your complete application and contact you within two weeks of receiving all materials. We invite you to explore our program pages at avalon.edu/graduate or schedule a virtual information session with a program director. Our admissions team is happy to answer any questions about specific programs, prerequisites, or the application timeline."""),

    ("EM-OL-SFS-Payment-Plan",
     "SFS","OL","Enrolled Undergrad",
     "Flexible Payment Plan Options Available for This Semester",
     "Spread your tuition balance into manageable installments",
     """Dear {first_name}, we understand that managing the cost of higher education requires careful planning, and Avalon University is committed to making your education as accessible as possible. If you have a remaining balance after financial aid has been applied, you may be eligible to enroll in one of our interest-free tuition payment plans for the current semester. The standard plan divides your balance into four equal monthly installments due on the first of each month. A one-time enrollment fee of $35 applies per semester. To enroll, log into your student portal, navigate to Billing and Payments, and select Payment Plan Enrollment. Enrollment for this semester's plan closes on the 15th of this month, and your first payment will be due at the time of enrollment. Students who enroll in a payment plan are not required to pay their full balance by the tuition due date, provided they remain current on all installment payments. If you anticipate difficulty meeting your payment obligations, please contact the Student Financial Services office before missing a payment — we have additional hardship assistance options available and want to work with you before your account is referred to collections. For questions about your balance, available aid, or payment options, contact us at financialaid@avalon.edu or call 800-555-0100."""),
]

CAMPUS_COPY = {
    "campus-hero-01.jpg": "Aerial view of Avalon University's main campus quad on a sunny fall afternoon, featuring red brick academic buildings surrounded by mature oak trees and students walking between classes.",
    "campus-hero-02.jpg": "Wide-angle view of the Avalon University library entrance with students studying on the outdoor steps and the university bell tower visible in the background.",
    "graduation-hero-01.jpg": "Hundreds of Avalon University graduates in full regalia celebrating at the outdoor commencement ceremony, mortar boards flying in the air against a bright blue sky.",
    "graduation-banner-01.jpg": "Close-up banner shot of smiling graduates in burgundy and gold regalia shaking hands with the university president on the commencement stage.",
    "student-cta-01.jpg": "Two Avalon University students collaborating at a laptop in the campus coffee shop, textbooks open, relaxed and engaged in their work.",
    "student-cta-02.jpg": "A first-generation college student in a university sweatshirt smiling at the camera in front of the admissions building, holding their acceptance letter.",
    "financial-doc-01.jpg": "Clean, professional close-up of a FAFSA and financial aid award letter on a desk with a laptop showing the student portal in the background.",
    "military-student-01.jpg": "An active-duty service member in uniform shaking hands with an Avalon University admissions counselor at a military education fair.",
    "campus-building-01.jpg": "The newly renovated Harmon Hall academic building at dusk, lights glowing from inside the modern glass-and-brick facade.",
    "intl-student-01.jpg": "A group of international students at Avalon University's cultural welcome event, holding flags from their home countries outside the student union.",
    "grad-student-01.jpg": "A graduate student presenting research findings to a small seminar group in one of Avalon's modern collaborative classroom spaces.",
    "alumni-event-01.jpg": "Avalon University alumni mingling at the annual homecoming networking reception in the university ballroom.",
}

SMS_DATA = [
    ("SMS-UC-REG-OpenReg-Reminder","UC","Enrolled Undergrad",
     "Registration opens tomorrow for Avalon University students. Log in to your portal now to review your degree audit and prepare your course selections. Questions? Contact advising@avalon.edu."),
    ("SMS-MIL-SFS-TADeadline","MIL","Enrolled Undergrad",
     "Reminder: Your Tuition Assistance authorization deadline is in 3 days. Contact military@avalon.edu or call 800-555-0200 to avoid a gap in your benefits."),
    ("SMS-OL-ADM-AppDecision","OL","Inquired Undergrad",
     "Your Avalon University admission decision is ready. Check your email and log in to apply.avalon.edu to view your offer and next steps."),
    ("SMS-UC-EVT-OpenHouse","UC","Inquired Undergrad",
     "Avalon University Open House is this Saturday, 10AM–3PM on the main campus. Meet faculty, tour facilities, and speak with current students. RSVP at avalon.edu/openhouse."),
    ("SMS-GC-AV-GradePosted","GC","Enrolled Graduate",
     "Your final grades for this term have been posted in the Avalon University student portal. Review them at portal.avalon.edu and contact your advisor with any questions."),
    ("SMS-INTL-ADM-I20Ready","INTL","Applied Undergrad",
     "Your Avalon University Form I-20 is ready. Log in to the International Student Portal to download your document and review next steps for your visa appointment."),
]

LP_DATA = [
    ("AU-UC-TRA-Accept-Landing","UC","Applied Undergrad",
     "https://apply.avalon.edu/uc-transfer-accept","Published","Admissions/Transfer",
     """Welcome to Avalon University — we are thrilled to offer you admission to our community of curious, driven, and passionate learners. This page is your personalized enrollment hub, designed to walk you through every step you need to take before your first day of classes. Your next steps include submitting your enrollment deposit, completing the FAFSA to unlock your financial aid offer, scheduling your academic advising appointment, and registering for New Student Orientation. Each step is outlined below with direct links to get started. Submitting your $200 enrollment deposit reserves your place in the incoming class and unlocks access to housing selection, course registration, and orientation sign-up. Your deposit is applied toward your first semester tuition balance. If you have already received your financial aid offer, you can review it in the Financial Aid portal and accept or decline individual awards. If you have not yet received an offer, completing the FAFSA at studentaid.gov is the fastest way to initiate the process — use Avalon's school code 004821. Transfer students may be eligible for up to 90 credits of transfer credit toward their degree. Your transfer credit evaluation will be completed within 10 business days of receiving your official transcripts. Your academic advisor will contact you within one week of your deposit to schedule your advising and registration appointment. We cannot wait to welcome you to campus this fall."""),

    ("AU-UC-FY-Accept-Landing","UC","Applied Undergrad",
     "https://apply.avalon.edu/uc-first-year-accept","Published","Admissions/First-Year",
     """Congratulations on your acceptance to Avalon University — this is the beginning of an extraordinary chapter. This personalized page will guide you through everything you need to do to complete your enrollment and prepare for your first semester on campus. Your checklist includes five key steps: submit your enrollment deposit, complete the FAFSA, attend an Admitted Student Day, submit your final high school transcript, and complete your housing application if you plan to live on campus. We know this is a lot to navigate, and we want you to know that our admissions team is here to help every step of the way. Your enrollment deposit of $200 reserves your spot in the Class of 2029 and is the single most important action you can take right now. Once your deposit is submitted, you will receive login credentials to the first-year student onboarding portal where you can access orientation registration, housing selection, and your NetID setup guide. The FAFSA is free to complete and takes approximately 30 minutes. Submitting it early ensures you receive the most complete financial aid offer possible before making your final enrollment decision. Avalon University meets 100% of demonstrated financial need for domestic students with four or more years of continuous enrollment. We invite you to visit campus for an Admitted Student Day — these events include tours, panel discussions with current students, department open houses, and lunch with your future classmates. Reserve your spot at avalon.edu/admitted."""),

    ("AU-OL-INQ-Online-Programs","OL","Inquired Undergrad",
     "https://online.avalon.edu/programs","Published","Online/Prospective",
     """Avalon University's online degree programs are built for people who are serious about their education and serious about their lives. Our online students include working professionals, parents, veterans, career changers, and students who simply prefer the flexibility of learning on their own schedule. All of our online programs are fully accredited and taught by the same faculty who teach on campus. You will never take a course from an adjunct hired specifically for online delivery — you will learn from faculty who are active researchers, published authors, and industry practitioners. Our online undergraduate programs include Business Administration, Computer Science, Healthcare Management, Psychology, Criminal Justice, and Communication Studies, among others. Each program can be completed in as few as two years for transfer students with significant prior credit. New courses start every eight weeks, so you can begin your education almost any time of year without waiting for a traditional semester to begin. Tuition for online programs is $350 per credit hour, and most students qualify for some form of financial aid. Military students using Tuition Assistance or GI Bill benefits will find that Avalon's tuition is fully covered under most benefit packages. Request information today and an enrollment advisor will contact you within one business day to discuss your goals, review your transfer credits, and walk you through the application process. There is no application fee and no minimum GPA requirement for most programs."""),

    ("AU-MIL-TA-Benefits-Guide","MIL","Inquired Undergrad",
     "https://military.avalon.edu/tuition-assistance","Published","Military/Benefits",
     """Avalon University is proud to serve those who serve our country. We have been a military-friendly institution for over 20 years, and we have helped thousands of active duty service members, veterans, and their families earn their degrees using military educational benefits. This page is your complete guide to using Tuition Assistance (TA) and GI Bill benefits at Avalon University. Tuition Assistance is available to active duty members of the Army, Navy, Marine Corps, Air Force, Space Force, and Coast Guard. TA covers up to $250 per credit hour and up to $4,500 per fiscal year. Avalon University's tuition for military students is set at $250 per credit hour — meaning your TA benefit covers your full tuition with no out-of-pocket cost for most programs. GI Bill Chapter 33 (Post-9/11) students receive tuition coverage, a housing allowance based on the ZIP code of the campus, and a book stipend of up to $1,000 per year. Avalon participates in the Yellow Ribbon Program, which means we cover any tuition costs that exceed the GI Bill cap at no additional charge to the student. To begin using your benefits, contact your Education Services Officer (ESO) or visit your branch's education portal to request TA authorization. Our military admissions team will help you navigate the paperwork and ensure your benefits are applied correctly from day one. We also offer priority registration, a dedicated military student lounge, peer mentorship, and an active student veterans organization on campus."""),

    ("AU-GC-Program-Finder","GC","Inquired Graduate",
     "https://graduate.avalon.edu/programs","Draft","Graduate/Prospective",
     """Avalon University's graduate programs are designed for professionals who are ready to advance their careers, deepen their expertise, or make a meaningful pivot into a new field. We offer master's degrees and doctoral programs across 12 schools and colleges, with options for full-time, part-time, evening, weekend, and fully online study. Whether you are looking to move into leadership, conduct original research, or earn the credentials required for licensure in your profession, Avalon has a graduate program designed with your goals in mind. Our most popular graduate programs include the Master of Business Administration with concentrations in Finance, Marketing, and Healthcare Management; the Master of Education with tracks in Curriculum Design and Educational Leadership; the Master of Science in Data Science and Artificial Intelligence; and the Doctor of Nursing Practice. All graduate programs are accredited by their respective professional accreditation bodies in addition to Avalon's regional accreditation. Class sizes in our graduate programs average 14 students, creating an intimate learning environment where faculty know you by name and professional networking happens naturally. Graduate assistantships are available in most doctoral programs and provide full tuition remission plus a monthly stipend. For master's students, graduate scholarships averaging $8,000 per year are available based on academic achievement and professional promise. Use the program finder below to explore options by field of study, format, and credential type. An admissions counselor is available to answer your questions by phone, email, or virtual appointment seven days a week."""),

    ("AU-INTL-Admissions","INTL","Applied Undergrad",
     "https://international.avalon.edu/admissions","Published","International/Admissions",
     """Welcome to Avalon University's International Admissions portal. We are home to students from more than 80 countries, and our campus is one of the most culturally diverse in the region. International students bring unique perspectives that enrich every classroom and every research project, and we are committed to providing you with the support you need to thrive academically and personally in a new country. This page walks you through the complete admissions process for international undergraduate students, including application requirements, English proficiency standards, financial documentation, and the I-20 and visa process. To apply, you will need to submit your completed application, official transcripts with certified English translations, a personal statement of 500 to 750 words, and evidence of English proficiency through TOEFL (minimum 80 iBT) or IELTS (minimum 6.5 overall). Avalon University evaluates international transcripts through our in-house credential evaluation team at no additional cost to applicants. Admission decisions are typically issued within three weeks of receiving a complete application. Once admitted, you will receive instructions for submitting your financial documentation — you must demonstrate the ability to cover one full year of tuition, housing, and living expenses. Upon receipt of financial documents, we will issue your Form I-20, which you will use to pay the SEVIS fee and schedule your F-1 visa interview. Our International Student Services office provides comprehensive pre-arrival guidance, an international student orientation, ESL support services, and ongoing immigration advising throughout your studies."""),

    ("AU-UC-Housing-App","UC","Enrolled Undergrad",
     "https://housing.avalon.edu/apply","Published","Housing/Residential",
     """Living on campus at Avalon University is one of the best decisions you can make as a new student. Research consistently shows that residential students earn higher GPAs, graduate at higher rates, and report stronger sense of belonging than commuter students. Our residential communities are designed to create meaningful connections — with your roommates, your neighbors, your resident advisors, and the broader campus community. Avalon offers nine residential communities ranging from traditional double-occupancy residence halls to suite-style and apartment-style living for upperclassmen. First-year students are required to live on campus for their first two semesters unless they are commuting from a parent or guardian's permanent residence within 30 miles of campus. Housing applications are available starting February 1st for the following fall semester, and room assignments are made on a rolling basis — applying early significantly improves your chances of getting your preferred room type and community. The housing application requires a $150 housing deposit, which is applied toward your housing fee. All residential students are required to participate in a meal plan. Three meal plan options are available, ranging from the 14-meal-per-week plan to the unlimited plan. Residence Life programming includes weekly community events, leadership development workshops, wellness programming, and academic support study nights. Each residential community is staffed by trained Resident Advisors who are available to help with everything from roommate conflicts to mental health resources. Apply for housing through the Student Portal or at housing.avalon.edu."""),

    ("AU-UC-Career-Services","UC","Continuing Undergrad",
     "https://careers.avalon.edu","Published","Career/Services",
     """The Avalon University Career and Employment Center is your partner from day one through graduation and beyond. Whether you are exploring career paths, preparing for your first internship, or conducting a full-time job search in your senior year, our team of career coaches and employer relations staff are here to help you succeed. Our services include one-on-one career coaching, resume and cover letter review, interview preparation, job shadow programs, internship placement, and on-campus recruiting. We host two major career fairs per year — one in September and one in February — with more than 150 employers attending each event. In addition, we host industry-specific networking nights, employer information sessions, and alumni mentor matching throughout the academic year. Avalon graduates are employed or enrolled in graduate school within six months of graduation at a rate of 94%. Our top employer partners include regional and national firms in healthcare, technology, education, financial services, and nonprofit management. Students in all majors and class years are encouraged to begin working with the Career Center early — students who engage with career services in their first year are significantly more likely to secure internships and full-time positions in their desired field. The Avalon Career Portal at careers.avalon.edu is your hub for job and internship postings, event registration, appointment scheduling, and career assessment tools. Walk-in advising hours are available Monday through Thursday from 1:00 to 4:00 PM, and virtual appointments are available on Fridays."""),
]

CB_DATA = [
    ("CB-HDR-UnivHeader","UC","Email Header",
     "Header/Global",
     "Avalon University",
     "Global email header with university logo and navigation links.",
     "%%[ var @firstname set @firstname = AttributeValue('Preferred_First_Name__c') IF EMPTY(@firstname) THEN SET @firstname = AttributeValue('FirstName') ENDIF ]%%",
     "/images/campus-hero-01.jpg",
     f"{UNIV_URL}, {UNIV_URL}/portal, {UNIV_URL}/my-courses",
     "registrar@avalon.edu, advising@avalon.edu"),

    ("CB-FTR-UnivFooter","UC","Email Footer",
     "Footer/Global",
     f"Questions? Contact Avalon University Student Services at 800-555-0100 or studentservices@{UNIV_DOMAIN}. To manage your email preferences or unsubscribe, click here. {UNIV} | 1 University Drive | Lakewood, CA 90000 | {UNIV_URL}",
     "Global email footer with contact info, unsubscribe link, and address.",
     "%%[ var @subkey set @subkey = _subscriberkey ]%% %%unsub_center_url%%",
     "",
     f"{UNIV_URL}/unsubscribe, {UNIV_URL}/privacy, {UNIV_URL}/contact",
     f"studentservices@{UNIV_DOMAIN}"),

    ("CB-SFS-FAFSAReminder","UC","FAFSA Reminder Block",
     "SFS/Financial-Aid",
     f"Complete your FAFSA today to ensure you receive maximum financial aid consideration from {UNIV}. The FAFSA is free, takes about 30 minutes, and is the only way to access federal grants, loans, and work-study. {UNIV}'s school code is 004821. Visit studentaid.gov to get started.",
     "Reusable FAFSA reminder block used in SFS email campaigns.",
     "%%[ var @firstname set @firstname = AttributeValue('Preferred_First_Name__c') IF EMPTY(@firstname) THEN SET @firstname = AttributeValue('FirstName') ENDIF var @aidyear set @aidyear = '2025-26' ]%%",
     "/images/financial-doc-01.jpg",
     "https://studentaid.gov, https://studentaid.gov/h/apply-for-aid/fafsa",
     f"financialaid@{UNIV_DOMAIN}"),

    ("CB-ADV-AdvisingCTA","UC","Advising Call-to-Action",
     "Advising/CTA",
     "Your academic advisor is here to help you stay on track, plan your schedule, and navigate any challenges you encounter during your studies. Schedule a same-day appointment online or call the Advising Center at 800-555-0300. Walk-in hours are available Monday through Thursday, 1PM to 4PM.",
     "Reusable advising CTA block for academic communications.",
     "%%[ var @advisorname set @advisorname = AttributeValue('Academic_Advisor_Name__c') IF EMPTY(@advisorname) THEN SET @advisorname = 'your academic advisor' ENDIF ]%%",
     "/images/student-cta-01.jpg",
     f"{UNIV_URL}/advising, {UNIV_URL}/advising/schedule",
     f"advising@{UNIV_DOMAIN}"),

    ("CB-MIL-VABenefitsCTA","MIL","VA Benefits CTA",
     "Military/Benefits",
     "Are you using VA education benefits or Tuition Assistance? Our Military Student Services team specializes in helping you navigate every step of the process — from obtaining your Certificate of Eligibility to submitting TA authorization and understanding your Yellow Ribbon benefits. Contact us at military@avalon.edu or call 800-555-0200.",
     "Reusable military benefits CTA used in MIL communications.",
     "%%[ var @branch set @branch = AttributeValue('Military_Branch__c') IF EMPTY(@branch) THEN SET @branch = 'your branch' ENDIF ]%%",
     "/images/military-student-01.jpg",
     f"{UNIV_URL}/military, {UNIV_URL}/military/benefits",
     f"military@{UNIV_DOMAIN}"),

    ("CB-EVT-OpenHouseCTA","UC","Open House CTA Block",
     "Events/Open-House",
     "Experience Avalon University for yourself. Campus Open House events are held every Saturday in October and November, featuring guided tours, faculty Q&A sessions, financial aid workshops, and lunch with current students. Reserve your spot at avalon.edu/openhouse — space is limited.",
     "Open house registration CTA block for prospective student emails.",
     "%%[ var @eventdate set @eventdate = LookupRows('Open_House_Dates','Active','True') ]%%",
     "/images/campus-hero-02.jpg",
     f"{UNIV_URL}/openhouse, {UNIV_URL}/visit",
     f"admissions@{UNIV_DOMAIN}"),

    ("CB-GR-CommencementInfo","GC","Commencement Info Block",
     "Events/Commencement",
     "Commencement is one of the most memorable days of your academic journey, and we want to make sure everything goes smoothly. Ceremony check-in opens at 8:30 AM. Graduates should wear full academic regalia. Each graduate may invite up to four guests. Parking is available in Lots C and D with a free shuttle to the Events Center. Order your regalia at the campus bookstore or at avalonbookstore.com.",
     "Reusable commencement info block for GC graduate communications.",
     "%%[ var @graddate set @graddate = AttributeValue('Graduation_Date__c') var @programname set @programname = AttributeValue('Program_Name__c') ]%%",
     "/images/graduation-hero-01.jpg",
     f"{UNIV_URL}/commencement, {UNIV_URL}/commencement/regalia, {UNIV_URL}/parking",
     f"graduation@{UNIV_DOMAIN}"),

    ("CB-VOC-SurveyLink","UC","VOC Survey Link Block",
     "VOC/Feedback",
     "Submit your VOC feedback. We value your perspective and use your responses to continuously improve the Avalon experience. Your survey takes less than 3 minutes and your responses are confidential. Click below to share your feedback.",
     "Voice of customer survey link block, embedded in post-send emails.",
     "%%[ var @surveyurl set @surveyurl = LookUp('Survey_Links_DE','URL','Subscriber_Key',_subscriberkey) var @subkey set @subkey = _subscriberkey ]%%",
     "",
     f"{UNIV_URL}/survey, {UNIV_URL}/feedback",
     f"feedback@{UNIV_DOMAIN}"),

    ("CB-SFS-PaymentPlanCTA","OL","Payment Plan CTA",
     "SFS/Billing",
     "Looking for flexible tuition payment options? Avalon University's interest-free payment plan lets you divide your semester balance into four equal monthly installments for a one-time $35 enrollment fee. Log into the Student Portal and navigate to Billing and Payments to enroll before the 15th of this month.",
     "Payment plan enrollment CTA for SFS billing communications.",
     "%%[ var @balance set @balance = LookUp('Student_Balance_DE','Balance','Colleague_ID',AttributeValue('Colleague_ID__c')) ]%%",
     "",
     f"{UNIV_URL}/billing, {UNIV_URL}/billing/payment-plan",
     f"billing@{UNIV_DOMAIN}"),

    ("CB-INTL-I20StatusBlock","INTL","I-20 Status Block",
     "International/Immigration",
     "Your Form I-20 status has been updated. Log in to the International Student Portal to view your current document, check your SEVIS record status, and access next steps for your visa appointment. If you need assistance, contact the Office of International Student Services at international@avalon.edu.",
     "I-20 and immigration status update block for international student emails.",
     "%%[ var @sevisstatus set @sevisstatus = LookUp('SEVIS_Status_DE','Status','Subscriber_Key',_subscriberkey) ]%%",
     "/images/intl-student-01.jpg",
     f"{UNIV_URL}/international, {UNIV_URL}/international/i20",
     f"international@{UNIV_DOMAIN}"),
]

AUTOMATION_DATA = [
    ("AU-UC-INTL-APP-AIP-ACC-FY25-July","UC","Inquired Undergrad","scheduled","Paused",
     "Jul 22 2025 9:30AM","Weekly","Targets newly admitted international students with acceptance nurture sequence"),
    ("Adhoc-AU-UC-FY-ACC-Deposit-Deadline-25FA","UC","Applied Undergrad","scheduled","Paused",
     "Apr 30 2025 9:30AM","Once","One-time send to pending depositors approaching the enrollment deadline"),
    ("AU-MIL-SFS-VA-Benefits-Weekly","MIL","Inquired Undergrad","scheduled","Active",
     "Mon 8:00AM","Weekly","Weekly enrollment of military inquiries into VA benefits nurture journey"),
    ("AU-OL-ADM-Application-Daily","OL","Inquired Undergrad","scheduled","Active",
     "Daily 7:00AM","Daily","Daily refresh of online inquiries for application nurture journey"),
    ("AU-GC-AV-Commencement-YOY","GC","Enrolled Graduate","scheduled","Active",
     "Mar 1 Annually","Once","Annual one-time trigger for commencement announcement to eligible graduates"),
    ("AU-UC-REG-Registration-Reminder-25FA","UC","Continuing Undergrad","scheduled","Active",
     "Daily 6:00AM","Daily","Daily audience refresh driving registration reminder sends each fall"),
    ("AU-INTL-ADM-Visa-Weekly","INTL","Applied Undergrad","scheduled","Active",
     "Wed 9:00AM","Weekly","Weekly refresh of international admitted students for visa guidance journey"),
    ("AU-UC-SFS-FAFSA-Campaign-25FA","UC","Applied Undergrad","scheduled","Stopped",
     "Daily 8:00AM","Daily","FAFSA campaign audience refresh — stopped after financial aid deadline passed"),
    ("AU-OL-INQ-NurtureFlow-Daily","OL","Inquired Undergrad","scheduled","Active",
     "Daily 5:00AM","Daily","Daily online inquiry population refresh for 8-touch nurture journey"),
    ("AU-MIL-ADM-TA-Benefits-Monthly","MIL","Inquired Undergrad","scheduled","Active",
     "1st of Month 7:00AM","Monthly","Monthly refresh of military prospects for TA benefits education series"),
    ("AU-UC-HSG-HousingApp-Reminder-25FA","UC","Enrolled Undergrad","scheduled","Active",
     "Weekly Mon 8:00AM","Weekly","Weekly housing application reminder for new admits who have not yet applied"),
    ("AU-GC-ADM-GradInfo-Monthly","GC","Inquired Graduate","scheduled","Active",
     "15th of Month 9:00AM","Monthly","Monthly graduate inquiry nurture audience refresh"),
    ("AU-INTL-SFS-Scholarship-Once","INTL","Applied Undergrad","scheduled","Stopped",
     "Jan 15 2025 9:00AM","Once","One-time scholarship announcement to international admits — completed"),
    ("AU-UC-CAR-Internship-Semester","UC","Continuing Undergrad","scheduled","Active",
     "Weekly Tue 7:00AM","Weekly","Weekly internship opportunity alerts to eligible undergrads"),
    ("Adhoc-AU-GC-Commencement-Survey-25SP","GC","Enrolled Graduate","scheduled","Stopped",
     "May 20 2025 10:00AM","Once","One-time post-commencement survey trigger — completed 25SP"),
]

SQL_QUERY_DATA = [
    ("SQ-UC-UG-Enrolled-ActiveStudents",
     "DE-UC-UG-Enrolled-Active",
     "Enrolled Undergrad",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.SNHUEmail AS InstitutionalEmail,
    s.PersonalEmail,
    s.campus,
    s.level,
    s.admitTerm,
    s.popselName,
    o.Program_Name__c,
    o.Stage_Name,
    o.Enrolled_Term__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-Active] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'UC'
  AND s.level = 'UG'
  AND o.Stage_Name = 'Enrolled'
  AND o.Enrolled_Term__c = '25FA'"""),

    ("SQ-OL-UG-Inquired-Last30Days",
     "DE-OL-UG-Inquired-Recent",
     "Inquired Undergrad",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.campus,
    s.level,
    s.admitTerm,
    s.popselName,
    o.Program_Interest__c,
    o.Lead_Source__c,
    o.CreatedDate
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-All] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'OL'
  AND s.level = 'UG'
  AND o.Stage_Name = 'Inquiry'
  AND DATEDIFF(DAY, o.CreatedDate, GETDATE()) <= 30"""),

    ("SQ-MIL-UG-Applied-NotYetEnrolled",
     "DE-MIL-UG-Applied-Pending",
     "Applied Undergrad",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.campus,
    s.Military_Branch__c,
    s.Benefit_Type__c,
    o.Stage_Name,
    o.Program_Name__c,
    o.admitTerm,
    o.Application_Complete_Date__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-All] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'MIL'
  AND o.Stage_Name IN ('Application','Admitted')
  AND o.admitTerm = '25FA'
  AND s.Benefit_Type__c IN ('VA','TA','YellowRibbon')"""),

    ("SQ-GC-GR-FirstTerm-ActiveJourney",
     "DE-GC-GR-FirstTerm-Active",
     "First Term Grad",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.SNHUEmail AS InstitutionalEmail,
    s.campus,
    s.level,
    o.Program_Name__c,
    o.Enrolled_Term__c,
    o.GPA__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-Active] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'GC'
  AND s.level = 'GR'
  AND o.Stage_Name = 'Enrolled'
  AND o.Enrolled_Term__c = '25FA'
  AND DATEDIFF(DAY, o.CreatedDate, GETDATE()) <= 120"""),

    ("SQ-UC-UG-StoppedOut-ReEngagement",
     "DE-UC-UG-StoppedOut-ReEngagement",
     "Stopped Out",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.campus,
    s.level,
    o.Program_Name__c,
    o.Last_Active_Term__c,
    o.Stop_Out_Reason__c,
    o.Credits_Completed__c,
    o.GPA__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-All] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'UC'
  AND o.Stage_Name = 'Stopped Out'
  AND o.Credits_Completed__c >= 30
  AND DATEDIFF(DAY, o.Last_Active_Term_End__c, GETDATE()) BETWEEN 90 AND 365"""),

    ("SQ-INTL-UG-Admitted-NoDeposit",
     "DE-INTL-UG-Admitted-NoDeposit",
     "Applied Undergrad",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.campus,
    s.Citizenship_Country__c,
    s.Visa_Type__c,
    o.Stage_Name,
    o.admitTerm,
    o.Program_Name__c,
    o.Admit_Date__c,
    o.Deposit_Date__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-All] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'INTL'
  AND o.Stage_Name = 'Admitted'
  AND o.Deposit_Date__c IS NULL
  AND o.admitTerm = '25FA'
  AND DATEDIFF(DAY, o.Admit_Date__c, GETDATE()) >= 7"""),

    ("SQ-UC-UG-RecentAlumni-2Years",
     "DE-UC-UG-RecentAlumni-2Years",
     "Recent Alumni",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.campus,
    o.Program_Name__c,
    o.Graduation_Date__c,
    o.GPA__c,
    o.Degree_Level__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-Graduated] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus IN ('UC','GC')
  AND o.Stage_Name = 'Graduated'
  AND DATEDIFF(YEAR, o.Graduation_Date__c, GETDATE()) <= 2"""),

    ("SQ-OL-UG-LapsedStudent-90to365Days",
     "DE-OL-UG-LapsedStudent",
     "Lapsed Student",
     """SELECT
    s.SubscriberKey,
    s.FirstName,
    s.LastName,
    s.Preferred_First_Name__c,
    s.PersonalEmail,
    s.campus,
    s.level,
    o.Program_Name__c,
    o.Last_Login_Date__c,
    o.Last_Active_Term__c,
    o.Credits_Completed__c
FROM [DE-Subscribers-Master] s
INNER JOIN [DE-Opportunities-All] o
    ON s.Colleague_ID__c = o.Colleague_ID__c
WHERE s.campus = 'OL'
  AND o.Stage_Name = 'Enrolled'
  AND DATEDIFF(DAY, o.Last_Login_Date__c, GETDATE()) BETWEEN 90 AND 365
  AND o.Registered_Next_Term__c = 'false'"""),
]

VOC_TEMPLATES = {
    "EM-SFS-UC-FAFSA-Available-Incoming": [
        ("positive","email_reply","Thank you so much for this reminder! I just finished my FAFSA — it was easier than I expected. Really appreciate how helpful the financial aid team has been throughout this process.",8,False),
        ("positive","survey","The FAFSA walkthrough video linked in this email was incredibly helpful. I was nervous about it but got it done in under 30 minutes.",9,False),
        ("positive","web_form","I completed my FAFSA right after getting this email. The instructions were clear and I felt supported. Looking forward to seeing my aid offer.",8,False),
        ("neutral","email_reply","I already submitted my FAFSA two weeks ago. Is there anything else I need to do to receive my financial aid offer?",None,False),
        ("neutral","survey","The email was clear but I'm still waiting for my Student Aid Report. How long does it usually take?",6,False),
        ("neutral","web_form","Received this email. I have a question about whether my parents' information is required since I'm considered independent.",None,True),
        ("negative","email_reply","I've received this same email four times now. I already submitted my FAFSA. Please update your records.",None,False),
        ("negative","survey","Why am I getting this? I graduated last year and no longer need financial aid information from Avalon.",2,False),
        ("negative","web_form","The link in the email goes to an error page. Please fix before sending again.",None,True),
    ],
    "EM-SFS-UC-Federal_Work_Study": [
        ("positive","email_reply","I'm so excited about the work-study opportunity! I just applied for the library position. Thank you for making the process so clear.",9,False),
        ("positive","survey","Work-study was one of the best parts of my freshman year. This email made it easy to understand how to get started.",8,False),
        ("positive","web_form","Applied for a position in the tutoring center right after reading this. The Workday portal was easy to navigate.",8,False),
        ("neutral","email_reply","How many hours per week am I allowed to work under work-study? I want to make sure it doesn't conflict with my course schedule.",None,False),
        ("neutral","survey","I got the email but I'm not sure I want to work on campus. Is it possible to defer the work-study award and use it as a grant instead?",5,False),
        ("neutral","web_form","Received this. I have a work-study award but I already have an off-campus job. Can I waive the work-study?",None,True),
        ("negative","email_reply","The positions listed on the portal are all already filled. There don't seem to be any openings available for first-year students.",None,True),
        ("negative","survey","I've been trying to complete my I-9 form for two weeks but can't get an appointment. This email is not helpful if the process is broken.",2,True),
        ("negative","web_form","Please stop sending me work-study emails. I declined this award when I accepted my financial aid package.",None,False),
    ],
    "EM-GC-AV-Commencement-Announcement": [
        ("positive","email_reply","I have been waiting for this email for five years. I am so proud and so grateful. Thank you to everyone at Avalon who supported me on this journey. See you at the ceremony!",10,False),
        ("positive","survey","This email had all the information I needed in one place. Ordered my regalia and RSVP'd my guests within 10 minutes of reading it. Beautifully organized.",9,False),
        ("positive","web_form","My family is flying in from three states away for this. Thank you for sending all the parking and shuttle details in advance — it will make the day so much smoother.",9,False),
        ("neutral","email_reply","I am completing my remaining coursework in the summer term. Can I still walk in the May ceremony even though my degree won't be conferred until August?",None,True),
        ("neutral","survey","The email was informative but I couldn't find clear instructions about hood colors for my specific degree program. Can you clarify?",6,False),
        ("neutral","web_form","I would like to request a fifth guest ticket. My mother, father, spouse, and two children would all like to attend. Is there a waitlist?",None,True),
        ("negative","email_reply","I graduated in December and did not receive any information about the spring ceremony until now. I had already made other plans for that weekend.",3,False),
        ("negative","survey","The online ticket system crashed when I tried to reserve my guest tickets. I ended up calling and waiting 45 minutes on hold.",2,True),
        ("negative","web_form","Please remove me from graduation communications. I have been a graduate for three years and keep receiving these emails each spring.",None,False),
    ],
    "EM-UC-AV-Final_Grades_Available": [
        ("positive","email_reply","Just checked my grades and I made the Dean's List! This has been an incredible semester. Thank you for the academic support resources.",10,False),
        ("positive","survey","I really appreciated the reminder about GPA requirements and the academic catalog link. Helpful for planning my spring schedule.",8,False),
        ("positive","web_form","Grades are up and I'm really proud of my progress this semester. The tutoring center made a huge difference. Thank you Avalon!",9,False),
        ("neutral","email_reply","One of my grades hasn't been posted yet and it's already been three days since final exams. Who should I contact?",None,True),
        ("neutral","survey","I received a grade I wasn't expecting. The email mentioned I could contact my advisor — do I need to do that before the grade appeal deadline?",5,True),
        ("neutral","web_form","I received a W in one of my courses. The email mentioned this would be on my transcript — will this affect my financial aid?",None,True),
        ("negative","email_reply","My grade in Chemistry is wrong. I submitted all assignments and my professor confirmed via email that I passed. This needs to be corrected immediately.",None,True),
        ("negative","survey","I've been on academic probation two semesters in a row and never received any proactive outreach from advising. The grades email is not enough support.",2,True),
        ("negative","web_form","Why did I receive this email? I withdrew from all courses this semester and was told I would be removed from academic communications.",1,False),
    ],
    "EM-OL-ADM-Application-Received": [
        ("positive","email_reply","Thank you for confirming receipt of my application. I feel reassured knowing there's a dedicated counselor assigned to my file. Looking forward to hearing back!",8,False),
        ("positive","survey","The application process was smooth and this confirmation email was exactly what I needed. Clear, professional, and warm.",9,False),
        ("positive","web_form","I've applied to several schools and this was by far the most professional and personable confirmation I received. Already impressed with Avalon.",8,False),
        ("neutral","email_reply","I submitted my transcripts through the portal but the application status still shows 'documents pending.' Has the review process begun?",None,True),
        ("neutral","survey","I applied three weeks ago and haven't heard from an admissions counselor yet. The email said 3-5 days — should I follow up?",5,True),
        ("neutral","web_form","I have a question about transfer credit evaluation. The email mentions it but doesn't explain the timeline.",None,True),
        ("negative","email_reply","I never applied to this school and have received multiple emails from you. Please remove me from your system immediately.",None,False),
        ("negative","survey","The portal link in the email doesn't work on mobile. I had to switch to a laptop just to check my application status.",3,True),
        ("negative","web_form","I applied over a month ago and still have not received any communication from an admissions counselor as promised in this email.",1,True),
    ],
}


def seed(conn):
    cur = conn.cursor()

    # ── 1. ACADEMIC TERMS ────────────────────────────────────
    print("Seeding academic_terms...")
    execute_values(cur, """
        INSERT INTO academic_terms
            (term_code,term_name,term_start_date,term_end_date,
             academic_year,season,audience_population,population_notes)
        VALUES %s ON CONFLICT DO NOTHING
    """, TERM_DATA)

    # ── 2. EMAIL ASSETS ──────────────────────────────────────
    print("Seeding email_assets...")
    email_rows = []
    email_asset_ids = []
    cb_ids_pool = [f"CB-{30000+i}" for i in range(len(CB_DATA))]

    for i, (name, dept, bu, audience, subject, preheader, copy) in enumerate(EMAIL_TEMPLATES):
        aid = f"EA-{10000+i}"
        email_asset_ids.append(aid)
        created = rand_ts(2022, 2023)
        modified = created + timedelta(days=random.randint(0, 400))
        creator = staff_name()
        modifier = staff_name()
        # pick 2-3 content blocks
        chosen_cbs = ",".join(random.sample(cb_ids_pool, min(3,len(cb_ids_pool))))
        img = list(CAMPUS_COPY.keys())[i % len(CAMPUS_COPY)]
        ampscript = (
            f"%%[ var @fn set @fn = AttributeValue('Preferred_First_Name__c') "
            f"IF EMPTY(@fn) THEN SET @fn = AttributeValue('FirstName') ENDIF "
            f"var @sid set @sid = _subscriberkey ]%%"
        )
        urls = f"{UNIV_URL},{UNIV_URL}/portal,{UNIV_URL}/{dept.lower()}"
        emails_found = f"{dept.lower()}@{UNIV_DOMAIN},registrar@{UNIV_DOMAIN}"
        email_rows.append((
            aid, f"LEG-{90000+i}", f"20250928_{350000+i}",
            bu, name, subject, preheader,
            "templatebasedemail", "207",
            f"Folder/{dept}", dept, audience,
            f"{dept.lower()}@{UNIV_DOMAIN}",
            f"{UNIV} {dept}",
            copy, ampscript,
            f"/images/{img}", urls, emails_found,
            chosen_cbs,
            creator, staff_email(creator),
            modifier, staff_email(modifier),
            created, modified,
            str(uuid.uuid4())
        ))
    execute_values(cur, """
        INSERT INTO email_assets
            (asset_id,legacy_id,unique_id,business_unit,name,
             subject_line,pre_header,asset_type_name,asset_type_id,
             folder,department_code,target_audience,
             sender_address,sender_name,copy_found,ampscript,
             images,urls_found,emails_found,content_blocks,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date,object_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, email_rows)

    # ── 3. IMAGE ASSETS ──────────────────────────────────────
    print("Seeding image_assets...")
    img_rows = []
    img_url_list = list(CAMPUS_COPY.keys())
    img_meta = {
        "campus-hero-01.jpg":     ("hero","campus","blue",True,False),
        "campus-hero-02.jpg":     ("hero","campus","blue",True,False),
        "graduation-hero-01.jpg": ("hero","graduation","warm",True,False),
        "graduation-banner-01.jpg":("banner","graduation","warm",True,True),
        "student-cta-01.jpg":     ("cta","student","neutral",True,False),
        "student-cta-02.jpg":     ("cta","student","warm",True,False),
        "financial-doc-01.jpg":   ("background","financial","neutral",False,False),
        "military-student-01.jpg":("hero","military","blue",True,False),
        "campus-building-01.jpg": ("background","campus","blue",False,False),
        "intl-student-01.jpg":    ("hero","student","neutral",True,True),
        "grad-student-01.jpg":    ("banner","student","neutral",True,False),
        "alumni-event-01.jpg":    ("hero","alumni","warm",True,False),
    }
    campaign_map = {
        "campus-hero-01.jpg":     ("Come to Campus Spring 2025","Your first day of classes is almost here","2025-04-24"),
        "campus-hero-02.jpg":     ("Campus Open House Fall 2024","Visit Avalon University this Saturday","2024-10-05"),
        "graduation-hero-01.jpg": ("Commencement Announcement 25SP","Your commencement ceremony details are here","2025-01-03"),
        "graduation-banner-01.jpg":("Graduate Celebration Week","Celebrate your achievement with the Avalon community","2025-05-10"),
        "student-cta-01.jpg":     ("Work-Study Awareness Campaign","You have been offered Federal Work-Study","2025-02-15"),
        "student-cta-02.jpg":     ("First Generation Student Welcome","Welcome to the Avalon family","2024-09-10"),
        "financial-doc-01.jpg":   ("FAFSA Awareness Campaign 25FA","The 2025-26 FAFSA is now available","2025-01-17"),
        "military-student-01.jpg":("Military Student Welcome Series","Your guide to Tuition Assistance at Avalon","2025-02-01"),
        "campus-building-01.jpg": ("Campus Renovation Announcement","See what's new at Avalon University","2024-11-20"),
        "intl-student-01.jpg":    ("International Student Welcome","Important visa and immigration information","2025-01-15"),
        "grad-student-01.jpg":    ("Graduate Program Spotlight","Advance your career with a graduate degree","2025-03-01"),
        "alumni-event-01.jpg":    ("Alumni Homecoming 2024","Join us for Avalon Homecoming Weekend","2024-10-18"),
    }
    for i, (fn, desc) in enumerate(CAMPUS_COPY.items()):
        itype, subj, color, people, textover = img_meta[fn]
        camp, subjectline, lastused = campaign_map[fn]
        email_id = email_asset_ids[i % len(email_asset_ids)]
        bu = random.choice(BUS_UNITS)
        ctr_base = {"hero":0.07,"banner":0.06,"cta":0.10,"background":0.04,"icon":0.05}.get(itype,0.06)
        or_base  = {"campus":0.31,"graduation":0.38,"student":0.29,"financial":0.26,"military":0.37,"alumni":0.24,"abstract":0.23}.get(subj,0.28)
        img_rows.append((
            f"/images/{fn}", email_id, itype, subj, color,
            people, textover,
            random.randint(80, 600),
            random.choice([600,800,1200,1440]),
            random.choice([300,400,600,800]),
            round(rand_rate(ctr_base,0.02),4),
            round(rand_rate(or_base,0.03),4),
            random.randint(2,22), bu,
            camp, subjectline,
            date.fromisoformat(lastused),
            desc
        ))
    execute_values(cur, """
        INSERT INTO image_assets
            (image_url,email_asset_id,image_type,subject_matter,
             primary_color,has_people,has_text_overlay,
             file_size_kb,width_px,height_px,
             avg_click_rate,avg_open_rate,usage_count,business_unit,
             campaign_name,email_subject_line,last_used_date,
             image_description)
        VALUES %s ON CONFLICT DO NOTHING
    """, img_rows)

    # ── 4. SMS ASSETS ────────────────────────────────────────
    print("Seeding sms_assets...")
    sms_asset_ids = []
    sms_rows = []
    for i, (name, bu, audience, msg) in enumerate(SMS_DATA):
        aid = f"SMS-{20000+i}"
        sms_asset_ids.append(aid)
        created = rand_ts(2023,2024)
        sms_rows.append((
            aid, bu, name, audience, msg,
            f"KW-{random.randint(1000,9999)}",
            f"8{random.randint(1000,9999)}",
            "US", True,
            staff_name(), staff_email(),
            staff_name(), staff_email(),
            created, created+timedelta(days=random.randint(0,180))
        ))
    execute_values(cur, """
        INSERT INTO sms_assets
            (asset_id,business_unit,name,target_audience,message_text,
             keyword_id,short_code,country_code,opt_in_configured,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, sms_rows)

    # ── 5. CONTENT BLOCK ASSETS ──────────────────────────────
    print("Seeding content_block_assets...")
    cb_rows = []
    for i, (aid_sfx, bu, name, folder, copy, desc, amp, img, urls, emails) in enumerate(CB_DATA):
        aid = f"CB-{30000+i}"
        created = rand_ts(2022,2023)
        version = str(random.randint(1,4))
        cb_rows.append((
            aid, f"20250928_CB{i}", bu, name,
            "contentblock", folder, str(30000+i), version,
            copy, amp, img, urls, emails,
            staff_name(), staff_email(),
            staff_name(), staff_email(),
            created, created+timedelta(days=random.randint(0,200))
        ))
    execute_values(cur, """
        INSERT INTO content_block_assets
            (asset_id,unique_id,business_unit,name,
             asset_type_name,folder_name,folder_id,version,
             copy_found,ampscript,images,urls_found,emails_found,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, cb_rows)

    # ── 6. LANDING PAGE ASSETS ───────────────────────────────
    print("Seeding landing_page_assets...")
    lp_rows = []
    for i, (name,bu,audience,url,status,folder,copy) in enumerate(LP_DATA):
        aid = f"LP-{40000+i}"
        created = rand_ts(2023,2024)
        pub_date = created+timedelta(days=random.randint(1,14)) if status=="Published" else None
        lp_rows.append((
            aid, f"20250928_LP{i}", bu, name, audience,
            name, url, status, "landingpage", folder, "1",
            pub_date, copy,
            True, True, True,
            staff_name(), staff_email(),
            staff_name(), staff_email(),
            created, created+timedelta(days=random.randint(0,300))
        ))
    execute_values(cur, """
        INSERT INTO landing_page_assets
            (asset_id,unique_id,business_unit,name,target_audience,
             page_name,page_url,published_status,
             asset_type_name,folder,version,
             published_date,copy_found,has_form,
             has_google_analytics,has_google_tag_manager,
             created_by_name,created_by_email,
             last_modified_by_name,last_modified_by_email,
             created_time,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, lp_rows)

    # ── 7. SQL QUERIES ───────────────────────────────────────
    print("Seeding sql_queries...")
    sq_rows = []
    for i, (name, target_de, audience, query_text) in enumerate(SQL_QUERY_DATA):
        qid = str(uuid.uuid4())
        sq_rows.append((
            qid, name, f"KEY-{name}",
            target_de, f"KEY-{target_de}",
            str(uuid.uuid4()), audience,
            1, "Update", random.randint(10000,99999),
            False, random.choice(BUS_UNITS),
            query_text,
            rand_ts(2022,2024), rand_ts(2024,2025)
        ))
    execute_values(cur, """
        INSERT INTO sql_queries
            (query_definition_id,name,key,
             target_name,target_key,target_id,
             target_description,
             target_update_type_id,target_update_type_name,
             category_id,is_frozen,business_unit,
             query_text,created_date,modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, sq_rows)

    # ── 8. AUTOMATIONS ───────────────────────────────────────
    print("Seeding automations...")
    auto_ids = []
    auto_rows = []
    for name, bu, audience, atype, status, schedule, freq, desc in AUTOMATION_DATA:
        aid = str(uuid.uuid4())
        akey = str(uuid.uuid4())
        auto_ids.append(aid)
        last_run = rand_ts(2025,2025)
        auto_rows.append((
            aid, akey, name, desc,
            bu, audience, 1, atype, 4, status,
            random.randint(10000,99999),
            schedule, last_run, str(uuid.uuid4())
        ))
    execute_values(cur, """
        INSERT INTO automations
            (automation_id,automation_key,name,description,
             business_unit,target_audience,type_id,type,
             status_id,status,category_id,
             schedule,last_run_time,last_run_instance_id)
        VALUES %s ON CONFLICT DO NOTHING
    """, auto_rows)

    # ── 9. AUTOMATION ACTIVITIES (linked to sql_queries) ─────
    print("Seeding automation_activities...")
    # fetch sql_query ids we just inserted
    cur.execute("SELECT query_definition_id, name, business_unit FROM sql_queries")
    sq_records = cur.fetchall()

    aa_rows = []
    for auto_id, (auto_name, bu, audience, *_) in zip(
            auto_ids, AUTOMATION_DATA):
        # each automation gets 1-2 SQL query activities
        num = random.randint(1,2)
        for step in range(1, num+1):
            sq = random.choice(sq_records)
            sq_id, sq_name, sq_bu = sq
            aa_rows.append((
                str(uuid.uuid4()),   # activity_id
                auto_id, auto_name,
                f"KEY-{auto_name[:30]}",
                step,
                sq_name,
                f"Audience query step {step} for {auto_name[:40]}",
                300,                 # 300 = SQL Query activity type in SFMC
                str(uuid.uuid4()),   # target DE id
                f"KEY-DE-{sq_name[:30]}",
                f"DE-{sq_name[:40]}",
                bu
            ))
    execute_values(cur, """
        INSERT INTO automation_activities
            (activity_id,automation_id,automation_key,
             automation_name,activity_step,activity_name,
             activity_description,activity_object_type_id,
             target_data_extension_id,
             target_data_extension_key,
             activity_data_extension_name,
             business_unit)
        VALUES %s ON CONFLICT DO NOTHING
    """, aa_rows)

    # ── 10. JOURNEYS ─────────────────────────────────────────
    print("Seeding journeys...")
    JOURNEY_TEMPLATES = [
        ("JB-FA-AWD-CFP-MIL-CollegeFinancingPlan","MIL","Stopped","Military","FA","25FA","Enrolled Undergrad"),
        ("JB-SFS-UC-Federal_Work_Study","UC","Active","Campus","SFS","25FA","Enrolled Undergrad"),
        ("JB-SFS-UC-Health_Insurance_Waiver","UC","Active","Campus","SFS","25FA","Enrolled Undergrad"),
        ("JB-UC-AV-Add_Drop_Deadline","UC","Stopped","Campus","Advising","25FA","Enrolled Undergrad"),
        ("JB-UC-AV-Final_Grades","UC","Active","Campus","Advising","25FA","Continuing Undergrad"),
        ("JB-UC-AV-Registration-Reminder-25FA","UC","Active","Freshman","Advising","25FA","Enrolled Undergrad"),
        ("JB-OL-ADM-Application-Nurture","OL","Active","Inquiry","Admissions","25FA","Inquired Undergrad"),
        ("JB-MIL-SFS-VA-Benefits-Onboard","MIL","Active","Military","SFS","25FA","Applied Undergrad"),
        ("JB-INTL-ADM-Visa-Requirements","INTL","Active","International","Admissions","25FA","Applied Undergrad"),
        ("JB-GC-AV-Commencement-Survey-YOY","GC","Active","Graduate","Advising","25SP","Enrolled Graduate"),
        ("JB-UC-SFS-FAFSA-Available-Incoming","UC","Stopped","Freshman","SFS","24FA","Applied Undergrad"),
        ("JB-OL-SFS-Payment-Plan-Reminder","OL","Active","Enrolled","SFS","25FA","Enrolled Undergrad"),
        ("JB-MIL-ADM-TA-Benefits-Guide","MIL","Active","Military","Admissions","25FA","Applied Undergrad"),
        ("JB-GC-ADM-Graduate-Program-Info","GC","Draft","Graduate","Admissions","25FA","Inquired Graduate"),
        ("JB-UC-HSG-Housing-Application-25FA","UC","Active","Freshman","Housing","25FA","Enrolled Undergrad"),
        ("JB-OL-UG-AlumniPush-ReEngagement","GC","Stopped","Alumni","Advising","24FA","Recent Alumni"),
        ("JB-INTL-SFS-Scholarship-Campaign","INTL","Active","International","SFS","25FA","Applied Graduate"),
        ("JB-UC-AV-Academic-Standing-Alert","UC","Active","Campus","Advising","25FA","Continuing Undergrad"),
        ("JB-OL-ADM-Deposit-Deadline-25FA","OL","Stopped","Applicant","Admissions","25FA","Applied Undergrad"),
        ("JB-UC-CAR-Internship-Spring-25","UC","Active","Senior","Career","25SP","Continuing Undergrad"),
    ]
    journey_ids = []
    j_rows = []
    for jname,bu,status,audience,dept,term,ta in JOURNEY_TEMPLATES:
        jid  = str(uuid.uuid4())
        jkey = str(uuid.uuid4())
        journey_ids.append(jid)
        created  = rand_ts(2022,2024)
        modified = created + timedelta(days=random.randint(1,500))
        j_rows.append((
            jid, jkey, jname,
            f"Journey for {ta} — {dept} department",
            bu, status, random.randint(1,3), 1.0,
            "SingleEntryAcrossAllVersions",
            str(uuid.uuid4()),
            modified, created,
            audience, dept, term, ta
        ))
    execute_values(cur, """
        INSERT INTO journeys
            (journey_id,journey_key,journey_name,description,
             business_unit,status,version,workflow_api_version,
             entry_mode,event_definition_id,
             last_modified_date,created_date,
             target_audience,department,academic_term,
             target_audience_detail)
        VALUES %s ON CONFLICT DO NOTHING
    """, j_rows)

    # ── 11. JOURNEY ENTRY SOURCES ────────────────────────────
    print("Seeding journey_entry_sources...")
    jes_rows = []
    for i, jid in enumerate(journey_ids):
        etype = random.choice(["AutomationAudience","EmailAudience","Schedule"])
        auto_id = random.choice(auto_ids) if etype=="AutomationAudience" else None
        start_ts = rand_ts(2024,2025)
        ta = JOURNEY_TEMPLATES[i][6]
        jes_rows.append((
            str(uuid.uuid4()), jid,
            JOURNEY_TEMPLATES[i][0],
            JOURNEY_TEMPLATES[i][1],
            etype,
            f"JB-EV-{JOURNEY_TEMPLATES[i][0][:30]}",
            str(uuid.uuid4()), str(uuid.uuid4()),
            f"DE-{JOURNEY_TEMPLATES[i][0][:40]}",
            auto_id, ta,
            "Production",
            random.choice(["Daily","Weekly","Once"]),
            start_ts,
            start_ts + timedelta(days=random.randint(30,365)),
            random.randint(1,7),
            staff_name(), staff_name()
        ))
    execute_values(cur, """
        INSERT INTO journey_entry_sources
            (entry_source_id,journey_id,journey_name,business_unit,
             entry_type,event_definition_key,
             event_definition_id,data_extension_id,data_extension_name,
             automation_id,target_audience,mode,schedule_frequency,
             schedule_start_time,schedule_end_time,schedule_occurrences,
             created_by,last_modified_by)
        VALUES %s ON CONFLICT DO NOTHING
    """, jes_rows)

    # ── 12. JOURNEY ACTIVITIES ───────────────────────────────
    print("Seeding journey_activities...")
    act_rows = []
    jact_for_metrics = []
    for i, (jid, (jname,bu,jstatus,audience,dept,term,ta)) in enumerate(
            zip(journey_ids, JOURNEY_TEMPLATES)):
        num_emails = random.randint(1,3)
        for step in range(num_emails):
            aid = str(uuid.uuid4())
            et  = EMAIL_TEMPLATES[i % len(EMAIL_TEMPLATES)]
            ea_ref = email_asset_ids[i % len(email_asset_ids)]
            ss  = "Active" if jstatus=="Active" else "Stopped"
            jact_for_metrics.append((
                aid, jid, jname, bu, ea_ref,
                et[0], et[4], audience, dept, ta
            ))
            act_rows.append((
                aid, jid, jname, str(uuid.uuid4()), bu,
                f"EMAILV2-{step+1}",
                f"Email Step {step+1}: {et[0][:40]}",
                "EMAIL",
                ea_ref, et[0], et[4], et[5],
                ss,
                str(uuid.uuid4()), str(uuid.uuid4()),
                True, True, True,
                f"AU-{jname[:30]}-step{step+1}",
                ta,
                staff_name(), rand_ts(2023,2024)
            ))
        if random.random() > 0.6 and sms_asset_ids:
            sms_aid = str(uuid.uuid4())
            act_rows.append((
                sms_aid, jid, jname, str(uuid.uuid4()), bu,
                "SMS-1", f"SMS Step: {jname[:40]}", "SMS",
                None,None,None,None,None,None,None,
                False,False,False,
                f"AU-{jname[:30]}-sms", ta,
                staff_name(), rand_ts(2023,2024)
            ))
    execute_values(cur, """
        INSERT INTO journey_activities
            (activity_id,journey_id,journey_name,activity_key,business_unit,
             activity_name,activity_description,activity_type,
             email_id,email_name,email_subject,email_pre_header,
             send_status,send_key,triggered_send_id,
             salesforce_tracking,send_logging,click_tracking,
             ga_campaign_name,target_audience,
             last_modified_by,last_modified_date)
        VALUES %s ON CONFLICT DO NOTHING
    """, act_rows)

    # ── 13. SUBSCRIBERS ──────────────────────────────────────
    print("Seeding subscribers (~5000)...")
    sub_rows = []
    sub_keys = []
    for i in range(5000):
        sk  = f"SUB-{100000+i}"
        sub_keys.append(sk)
        bu    = random.choice(BUS_UNITS)
        stype = random.choice(["Military","International","Domestic","Transfer"])
        slvl  = random.choice(["Freshman","Sophomore","Junior","Senior","Graduate","Doctoral"])
        stage = random.choice(["Inquiry","Applicant","Admitted","Enrolled","Alumni","Stopped"])
        ta    = random.choice(TARGET_AUDIENCES)
        term  = random.choice(["23FA","24SP","24FA","25SP","25FA"])
        sub_rows.append((
            sk, f"COL-{random.randint(1000000,9999999)}",
            fake.email(), fake.first_name(), fake.last_name(),
            fake.first_name() if random.random()>0.3 else None,
            bu, stage, stype, slvl, ta,
            bu[:2], bu[:2],
            "UG" if slvl in ["Freshman","Sophomore","Junior","Senior"] else "GR",
            term, rand_ts(2022,2025),
            f"POPSEL-{bu}-{stype[:3].upper()}-{term}",
            random.random()>0.1
        ))
    execute_values(cur, """
        INSERT INTO subscribers
            (subscriber_key,colleague_id,email,first_name,last_name,
             preferred_first_name,business_unit,student_stage,student_type,
             student_level,target_audience,campus,original_campus,level,
             admit_term,term_start_date,popsel_name,is_active_subscriber)
        VALUES %s ON CONFLICT DO NOTHING
    """, sub_rows)

    # ── 14. OPPORTUNITIES ────────────────────────────────────
    print("Seeding opportunities (~4000)...")
    programs = [
        "Business Administration","Computer Science","Psychology",
        "Healthcare Administration","Criminal Justice","Communication",
        "Information Technology","Accounting","Marketing","Education",
        "Data Science","Nursing","Social Work","Public Administration",
    ]
    opp_rows = []
    for sk in random.sample(sub_keys, 4000):
        term  = random.choice(["23FA","24SP","24FA","25SP","25FA"])
        stage = random.choice(["Application","Admitted","Enrolled","Registered"])
        ta    = random.choice(TARGET_AUDIENCES)
        opp_rows.append((
            sk, f"COL-{random.randint(1000000,9999999)}",
            stage, random.choice(programs),
            random.choice(["UG","GR"]),
            term, term if stage=="Enrolled" else None,
            ta,
            random.random()>0.3, random.random()>0.9,
            round(random.uniform(1.8,4.0),2)
        ))
    execute_values(cur, """
        INSERT INTO opportunities
            (subscriber_key,colleague_id,stage_name,program_name,
             program_level,admit_term,enrolled_term,target_audience,
             registered_next_term,withdrew,gpa)
        VALUES %s
    """, opp_rows)

    # ── 15. DOD_METRICS ──────────────────────────────────────
    print("Seeding dod_metrics (~70 000 rows)...")
    BASE_OR = {
        "Military":0.38,"International":0.32,"Freshman":0.29,
        "Senior":0.27,"Graduate":0.31,"Campus":0.28,
        "Transfer":0.26,"Alumni":0.22,"Inquiry":0.24,
    }
    metrics_rows = []
    for act_info in jact_for_metrics:
        act_id,jid,jname,bu,email_ref,email_name,subject,audience,dept,ta = act_info
        base_or  = BASE_OR.get(audience, 0.28)
        base_ctr = base_or * random.uniform(0.25,0.45)
        num_days = random.randint(30,90)
        start_d  = rand_date(2024,2025)
        for day_off in range(num_days):
            sd      = start_d + timedelta(days=day_off)
            sends   = random.randint(200,3000)
            deliv   = int(sends * rand_rate(0.97,0.01))
            opens   = int(deliv * rand_rate(base_or,0.05))
            u_opens = int(opens * rand_rate(0.75,0.08))
            clicks  = int(u_opens * rand_rate(base_ctr*2,0.04))
            u_clk   = int(clicks * rand_rate(0.70,0.08))
            bounces = sends - deliv
            unsubs  = max(0,int(sends * rand_rate(0.002,0.001)))
            or_c  = round(u_opens/deliv,6) if deliv>0 else 0
            ctr_c = round(u_clk/deliv,6)   if deliv>0 else 0
            dr_c  = round(deliv/sends,6)    if sends>0 else 0
            ctor  = round(u_clk/u_opens,6)  if u_opens>0 else 0
            br_c  = round(bounces/sends,6)  if sends>0 else 0
            jid_str = str(random.randint(3000000,3999999))
            metrics_rows.append((
                jid_str,
                f"{email_name}{sd.strftime('%b %d %Y %I:%M%p')}",
                f"{email_name}_{jid_str}_{sd.strftime('%Y%m%d')}",
                bu, email_name, email_ref,
                jname, jid,
                "Active" if random.random()>0.3 else "Stopped",
                random.randint(1,3),
                f"{jid}_{random.randint(1,3)}",
                f"{dept.lower()}@{UNIV_DOMAIN}",
                f"{UNIV} {dept}", subject,
                sd, sends, deliv, bounces,
                opens, u_opens, clicks, u_clk, unsubs,
                or_c, ctr_c, dr_c, ctor, br_c,
                audience, dept, ta
            ))
            if len(metrics_rows) >= 5000:
                execute_values(cur, """
                    INSERT INTO dod_metrics
                        (job_id,id_combo,unique_email_send,
                         business_unit,email_name,email_asset_id,
                         journey_name,journey_id,journey_status,
                         journey_version,unique_journey_id_version,
                         sender_address,sender_name,subject_line,send_date,
                         total_sends,deliveries,total_bounces,
                         total_opens,unique_opens,total_clicks,unique_clicks,
                         total_unsubscribes,
                         open_rate,click_rate,delivery_rate,
                         click_to_open_rate,bounce_rate,
                         target_segment,department_code,target_audience)
                    VALUES %s
                """, metrics_rows)
                conn.commit(); metrics_rows = []
    if metrics_rows:
        execute_values(cur, """
            INSERT INTO dod_metrics
                (job_id,id_combo,unique_email_send,
                 business_unit,email_name,email_asset_id,
                 journey_name,journey_id,journey_status,
                 journey_version,unique_journey_id_version,
                 sender_address,sender_name,subject_line,send_date,
                 total_sends,deliveries,total_bounces,
                 total_opens,unique_opens,total_clicks,unique_clicks,
                 total_unsubscribes,
                 open_rate,click_rate,delivery_rate,
                 click_to_open_rate,bounce_rate,
                 target_segment,department_code,target_audience)
            VALUES %s
        """, metrics_rows)

    conn.commit()

    # ── 16. VOC RESPONSES ────────────────────────────────────
    print("Seeding voc_responses...")
    # fetch metric IDs and their email_asset_id for linking
    cur.execute("""
        SELECT id, email_asset_id, email_name, business_unit, target_audience
        FROM dod_metrics
        ORDER BY RANDOM() LIMIT 500
    """)
    metric_sample = cur.fetchall()

    channels = ["email_reply","survey","web_form"]
    voc_rows = []

    for metric_id, ea_id, email_name, bu, ta in metric_sample:
        # find template key that best matches the email_name
        tpl_key = None
        for k in VOC_TEMPLATES:
            if k in email_name:
                tpl_key = k; break
        if not tpl_key:
            tpl_key = random.choice(list(VOC_TEMPLATES.keys()))

        templates = VOC_TEMPLATES[tpl_key]
        # pick ~1-3 responses per metric row
        chosen = random.sample(templates, min(random.randint(1,3), len(templates)))
        sub_key = random.choice(sub_keys)

        for sentiment, channel, text, score, follow_up in chosen:
            voc_rows.append((
                sub_key, ea_id, metric_id,
                rand_ts(2024,2025),
                channel, sentiment, text,
                score,
                sentiment=="negative" and "unsubscribe" in text.lower(),
                follow_up, None,
                bu, ta
            ))

    execute_values(cur, """
        INSERT INTO voc_responses
            (subscriber_key,email_asset_id,dod_metric_id,
             response_date,response_channel,sentiment,response_text,
             survey_score,unsubscribe_request,follow_up_required,
             follow_up_notes,business_unit,target_audience)
        VALUES %s
    """, voc_rows)

    conn.commit()
    cur.close()
    print("\n✅ Seed complete! Row counts:")
    cur2 = conn.cursor()
    for tbl in [
        "academic_terms","email_assets","sms_assets",
        "content_block_assets","landing_page_assets","image_assets",
        "automations","automation_activities","sql_queries",
        "journeys","journey_entry_sources","journey_activities",
        "subscribers","opportunities","dod_metrics","voc_responses",
    ]:
        cur2.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl}: {cur2.fetchone()[0]:,}")
    cur2.close()


if __name__ == "__main__":
    if not DATABASE_URL:
        print("❌  DATABASE_URL not set in .env")
        print("    postgresql://user:pass@host/dbname?sslmode=require")
        exit(1)
    conn = psycopg2.connect(DATABASE_URL)
    seed(conn)
    conn.close()
