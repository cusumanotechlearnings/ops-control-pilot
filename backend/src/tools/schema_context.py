"""
DATA QUERY AGENT -- SCHEMA CONTEXT
Paste this string into your data query agent's system prompt.
Claude reads this to understand the database before generating SQL.
"""

SCHEMA_CONTEXT = """
## DATABASE: Avalon University Marketing Operations (Neon Postgres) -- READ-ONLY

You have access to an execute_sql tool. Only use SELECT statements.
Never use INSERT, UPDATE, DELETE, DROP, or any write operation.

University: Avalon University | Domain: avalon.edu | Abbrev: AU

---

### TABLE: academic_terms
Reference data for academic terms, split by student population.
Multiple rows share the same term_code -- one per population.
Columns:
  term_code          VARCHAR  -- e.g. '25FA', '24SP', '23FA'
  term_name          VARCHAR  -- e.g. 'Fall 2025'
  term_start_date    DATE
  term_end_date      DATE
  academic_year      VARCHAR  -- e.g. 'FY2025'
  season             VARCHAR  -- 'Fall', 'Spring', 'Summer'
  audience_population VARCHAR -- 'Undergraduate', 'Graduate', 'PhD / Doctoral'
  population_notes   VARCHAR  -- format/pacing notes
Note: JOIN on both term_code AND audience_population for precise matching.

---

### TABLE: dod_metrics  <- PRIMARY FACT TABLE
Day-over-day email performance. One row per email per send date.
For multi-day analysis use AVG() on rates or SUM() on counts.
Columns:
  job_id                VARCHAR
  business_unit         ENUM      -- 'UC','GC','OL','MIL','INTL'
  email_name            VARCHAR   -- email asset name
  email_asset_id        VARCHAR   -- FK -> email_assets.asset_id
  journey_name          VARCHAR
  journey_id            VARCHAR   -- FK -> journeys.journey_id
  journey_status        ENUM      -- 'Active','Stopped','Draft','Paused','Complete'
  sender_address        VARCHAR
  subject_line          VARCHAR
  send_date             DATE
  total_sends           INTEGER
  deliveries            INTEGER
  total_bounces         INTEGER
  total_opens           INTEGER
  unique_opens          INTEGER
  total_clicks          INTEGER
  unique_clicks         INTEGER
  total_unsubscribes    INTEGER
  open_rate             DECIMAL   -- 0.0 to 1.0 (multiply by 100 for %)
  click_rate            DECIMAL
  delivery_rate         DECIMAL
  click_to_open_rate    DECIMAL
  bounce_rate           DECIMAL
  target_segment        VARCHAR   -- 'Military','Freshman','Graduate','Campus' etc
  department_code       VARCHAR   -- 'SFS','Advising','Admissions','FA','Career' etc
  target_audience       VARCHAR   -- 'Enrolled Undergrad','First Term Grad' etc (detailed)

---

### TABLE: email_assets
Email template definitions. One row per email.
Columns:
  asset_id              VARCHAR   -- primary key
  business_unit         ENUM
  name                  VARCHAR   -- full name e.g. 'EM-SFS-UC-FAFSA-Available-Incoming'
  subject_line          VARCHAR
  pre_header            VARCHAR
  department_code       VARCHAR   -- 'SFS','FA','Advising','Admissions','Career' etc
  target_audience       VARCHAR   -- intended audience
  sender_address        VARCHAR
  sender_name           VARCHAR
  copy_found            TEXT      -- substantive email body copy
  ampscript             TEXT      -- SFMC AMPscript personalization logic
  images                TEXT      -- image URLs used in this email
  urls_found            TEXT      -- URLs found in the email
  emails_found          TEXT      -- email addresses found in the email
  content_blocks        TEXT      -- comma-separated IDs -> content_block_assets.asset_id
  folder                VARCHAR
  created_by_name       VARCHAR
  last_modified_by_name VARCHAR
  created_time          TIMESTAMP
  last_modified_date    TIMESTAMP

---

### TABLE: journeys
Journey (automation flow) definitions.
Columns:
  journey_id            VARCHAR   -- primary key (UUID)
  journey_name          VARCHAR
  business_unit         ENUM
  status                ENUM      -- 'Active','Stopped','Draft','Paused','Complete'
  version               INTEGER
  target_audience       VARCHAR   -- high-level: 'Military','Graduate' etc
  target_audience_detail VARCHAR  -- detailed: 'Enrolled Undergrad' etc
  department            VARCHAR
  academic_term         VARCHAR   -- e.g. '25FA'
  created_date          TIMESTAMP
  last_modified_date    TIMESTAMP

---

### TABLE: journey_activities
Individual steps within journeys. Each send is one activity.
Columns:
  activity_id           VARCHAR
  journey_id            VARCHAR   -- FK -> journeys.journey_id
  journey_name          VARCHAR
  business_unit         ENUM
  activity_type         ENUM      -- 'EMAIL','SMS','WAIT','DECISIONSPLIT' etc
  email_id              VARCHAR   -- FK -> email_assets.asset_id (null if SMS)
  email_name            VARCHAR
  email_subject         VARCHAR
  send_status           ENUM
  target_audience       VARCHAR
  sms_asset_id          VARCHAR   -- FK -> sms_assets.asset_id (null if email)
  last_modified_date    TIMESTAMP

---

### TABLE: automations
Scheduled automation definitions that populate journeys.
Columns:
  automation_id         VARCHAR   -- primary key (UUID)
  name                  VARCHAR
  business_unit         ENUM
  target_audience       VARCHAR
  type                  VARCHAR   -- 'scheduled','triggered'
  status                ENUM      -- 'Active','Paused','Stopped','Scheduled','Building'
  schedule              VARCHAR   -- human-readable: 'Daily 7:00AM','Weekly Mon 8:00AM'
  last_run_time         TIMESTAMP
  description           TEXT

---

### TABLE: automation_activities
Individual SQL query steps within an automation.
Columns:
  activity_id                  VARCHAR   -- maps to sql_queries.query_definition_id
  automation_id                VARCHAR   -- FK -> automations.automation_id
  automation_name              VARCHAR
  activity_step                INTEGER   -- execution order
  activity_name                VARCHAR
  activity_description         TEXT
  activity_object_type_id      VARCHAR   -- 300 = SQL Query Activity
  activity_data_extension_name VARCHAR   -- target DE name
  business_unit                ENUM

---

### TABLE: sql_queries
SFMC SQL Activity definitions (written in SFMC bracket notation).
These define how audiences are built for journeys.
Columns:
  query_definition_id    VARCHAR   -- primary key (UUID)
  name                   VARCHAR
  target_name            VARCHAR   -- destination data extension name
  target_description     VARCHAR   -- audience description / target_audience label
  target_update_type_name VARCHAR  -- 'Update','Overwrite','Append'
  business_unit          ENUM
  query_text             TEXT      -- SFMC SQL using [DataExtension] bracket syntax
  created_date           TIMESTAMP
  modified_date          TIMESTAMP

---

### TABLE: journey_entry_sources
How journeys are triggered and populated.
Columns:
  entry_source_id        VARCHAR
  journey_id             VARCHAR   -- FK -> journeys.journey_id
  entry_type             ENUM      -- 'AutomationAudience','EmailAudience','Schedule'
  data_extension_name    VARCHAR
  automation_id          VARCHAR   -- FK -> automations.automation_id
  target_audience        VARCHAR
  schedule_frequency     ENUM      -- 'Daily','Weekly','Monthly','Once'
  schedule_start_time    TIMESTAMP
  schedule_end_time      TIMESTAMP

---

### TABLE: subscribers
Student/contact records.
Columns:
  subscriber_key         VARCHAR   -- primary key
  colleague_id           VARCHAR   -- internal student ID
  email                  VARCHAR
  first_name, last_name  VARCHAR
  preferred_first_name   VARCHAR
  business_unit          ENUM
  student_stage          ENUM      -- 'Inquiry','Applicant','Admitted','Enrolled','Alumni','Stopped'
  student_type           ENUM      -- 'Military','International','Domestic','Transfer'
  student_level          ENUM      -- 'Freshman','Sophomore','Junior','Senior','Graduate','Doctoral'
  target_audience        VARCHAR   -- 'Enrolled Undergrad','First Term Grad' etc
  campus                 VARCHAR
  level                  VARCHAR   -- 'UG' or 'GR'
  admit_term             VARCHAR
  is_active_subscriber   BOOLEAN

---

### TABLE: opportunities
Downstream funnel data -- what happened after emails were received.
Columns:
  subscriber_key         VARCHAR   -- FK -> subscribers.subscriber_key
  stage_name             VARCHAR   -- 'Application','Admitted','Enrolled','Registered'
  program_name           VARCHAR
  program_level          VARCHAR   -- 'UG','GR'
  admit_term             VARCHAR
  enrolled_term          VARCHAR
  target_audience        VARCHAR
  registered_next_term   BOOLEAN
  withdrew               BOOLEAN
  gpa                    DECIMAL

---

### TABLE: sms_assets
SMS message definitions.
Columns:
  asset_id, business_unit, name, target_audience,
  message_text, keyword_id, short_code,
  created_time, last_modified_date

---

### TABLE: landing_page_assets
Landing page definitions.
Columns:
  asset_id, business_unit, name, target_audience,
  page_name, page_url,
  published_status -- 'Published','Unpublished','Draft'
  has_form, has_google_analytics,
  copy_found TEXT -- substantive page copy
  folder, published_date, created_time, last_modified_date

---

### TABLE: content_block_assets
Reusable content blocks embedded in emails.
Columns:
  asset_id, business_unit, name, folder_name,
  copy_found TEXT -- block content
  ampscript TEXT  -- SFMC personalization logic
  images TEXT     -- image URLs (joins to image_assets.image_url)
  urls_found TEXT -- URLs in the block
  emails_found TEXT -- email addresses in the block
  created_time, last_modified_date

---

### TABLE: image_assets
Image metadata and historical performance.
Columns:
  image_url             VARCHAR   -- path e.g. '/images/campus-hero-01.jpg'
  email_asset_id        VARCHAR   -- FK -> email_assets.asset_id
  image_type            VARCHAR   -- 'hero','banner','icon','cta','background'
  subject_matter        VARCHAR   -- 'campus','student','graduation','financial','military' etc
  primary_color         VARCHAR   -- 'blue','warm','neutral' etc
  has_people            BOOLEAN
  has_text_overlay      BOOLEAN
  avg_click_rate        DECIMAL   -- historical CTR (0.0-1.0)
  avg_open_rate         DECIMAL   -- historical open rate
  usage_count           INTEGER
  business_unit         ENUM
  campaign_name         VARCHAR   -- e.g. 'Come to Campus Spring 2025'
  email_subject_line    VARCHAR   -- subject of email this image appeared in
  last_used_date        DATE
  image_description     TEXT      -- detailed visual description of the image

---

### TABLE: voc_responses
Voice of customer responses to email communications.
Columns:
  id                    SERIAL    -- primary key
  subscriber_key        VARCHAR   -- FK -> subscribers.subscriber_key
  email_asset_id        VARCHAR   -- FK -> email_assets.asset_id
  dod_metric_id         INTEGER   -- FK -> dod_metrics.id
  response_date         TIMESTAMP
  response_channel      VARCHAR   -- 'email_reply','survey','web_form'
  sentiment             VARCHAR   -- 'positive','neutral','negative'
  response_text         TEXT      -- verbatim VOC response
  survey_score          INTEGER   -- NPS/CSAT 1-10 (null if not a survey)
  unsubscribe_request   BOOLEAN
  follow_up_required    BOOLEAN
  follow_up_notes       TEXT
  business_unit         ENUM
  target_audience       VARCHAR

---

## TARGET AUDIENCE VALUES (standard set across all tables)
  'Enrolled Undergrad'     -- currently enrolled undergraduate students
  'First Term Grad'        -- graduate students in their first term
  'Applied Undergrad'      -- undergraduate applicants (pre-enrollment)
  'Recent Alumni'          -- graduated within last 2 years
  'Inquired Graduate'      -- graduate prospects who have shown interest
  'Enrolled Graduate'      -- currently enrolled graduate students
  'Applied Graduate'       -- graduate applicants (pre-enrollment)
  'Inquired Undergrad'     -- undergraduate prospects who have shown interest
  'Continuing Undergrad'   -- undergraduate students beyond first term
  'Stopped Out'            -- formally stopped with intent to return
  'ClosedLost'             -- exited funnel, not expected to return
  'Lapsed Student'         -- enrolled but disengaged, not formally withdrawn

---

## KEY RELATIONSHIPS
  dod_metrics.email_asset_id        -> email_assets.asset_id
  dod_metrics.journey_id            -> journeys.journey_id
  journey_activities.journey_id     -> journeys.journey_id
  journey_activities.email_id       -> email_assets.asset_id
  journey_entry_sources.journey_id  -> journeys.journey_id
  journey_entry_sources.automation_id -> automations.automation_id
  automation_activities.automation_id -> automations.automation_id
  automation_activities.activity_id -> sql_queries.query_definition_id
  opportunities.subscriber_key      -> subscribers.subscriber_key
  image_assets.email_asset_id       -> email_assets.asset_id
  content_block_assets (joined via email_assets.content_blocks CSV field)
  voc_responses.subscriber_key      -> subscribers.subscriber_key
  voc_responses.email_asset_id      -> email_assets.asset_id
  voc_responses.dod_metric_id       -> dod_metrics.id

---

## BUSINESS LOGIC RULES
1. 'Active' journeys = journeys.status = 'Active'
2. 'Automated' journeys = journey_entry_sources.entry_type = 'AutomationAudience'
3. Monthly aggregation: AVG(open_rate), SUM(total_sends) GROUP BY DATE_TRUNC('month', send_date)
4. Rates stored as decimals -- multiply by 100 for percentage display
5. Lift = difference between two groups' avg rates (e.g. SMS vs non-SMS journeys)
6. Military audience = target_segment = 'Military' OR business_unit = 'MIL' OR target_audience ILIKE '%Military%'
7. Graduate audience = student_level = 'Graduate' OR target_audience IN ('Enrolled Graduate','First Term Grad','Applied Graduate')
8. YOY comparison: JOIN academic_terms on send_date BETWEEN term_start_date AND term_end_date, filter by season
9. VOC sentiment analysis: GROUP BY sentiment, COUNT(*), AVG(survey_score)
10. Content block joins: email_assets.content_blocks is a CSV string of content_block_assets.asset_id values -- use ILIKE '%CB-XXXXX%' for joins
11. Image similarity lookup: match on image_type AND subject_matter AND has_people in image_assets
"""
