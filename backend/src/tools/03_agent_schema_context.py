"""
DATA QUERY AGENT -- SCHEMA CONTEXT
Paste this string into your data query agent's system prompt.
Claude reads this to understand the database before generating SQL.
"""

SCHEMA_CONTEXT = """
## DATABASE: Marketing Operations (Neon Postgres) -- READ-ONLY

You have access to a execute_sql tool. Only use SELECT statements.
Never use INSERT, UPDATE, DELETE, DROP, or any write operation.

---

### TABLE: academic_terms
Stores academic term reference data for YOY and term comparisons.
Columns:
  term_code       VARCHAR  -- e.g. '25FA', '24SP', '23FA'
  term_name       VARCHAR  -- e.g. 'Fall 2025'
  term_start_date DATE
  term_end_date   DATE
  academic_year   VARCHAR  -- e.g. 'FY2025'
  season          VARCHAR  -- 'Fall', 'Spring', 'Summer'

---

### TABLE: dod_metrics  ← PRIMARY FACT TABLE
Day-over-day email performance. One row per email per send date.
For multi-day aggregation, use AVG() on rates or SUM() on counts.
Columns:
  job_id                VARCHAR   -- SFMC job identifier
  business_unit         ENUM      -- 'UC','GC','OL','MIL','INTL'
  email_name            VARCHAR   -- email asset name
  email_asset_id        VARCHAR   -- FK → email_assets.asset_id
  journey_name          VARCHAR   -- parent journey name
  journey_id            VARCHAR   -- FK → journeys.journey_id
  journey_status        ENUM      -- 'Active','Stopped','Draft','Paused','Complete'
  sender_address        VARCHAR
  subject_line          VARCHAR
  send_date             DATE      -- the specific day this row represents
  total_sends           INTEGER
  deliveries            INTEGER
  total_bounces         INTEGER
  total_opens           INTEGER
  unique_opens          INTEGER   -- deduplicated openers
  total_clicks          INTEGER
  unique_clicks         INTEGER   -- deduplicated clickers
  total_unsubscribes    INTEGER
  open_rate             DECIMAL   -- unique_opens / deliveries (0.0 to 1.0)
  click_rate            DECIMAL   -- unique_clicks / deliveries (0.0 to 1.0)
  delivery_rate         DECIMAL   -- deliveries / total_sends
  click_to_open_rate    DECIMAL   -- unique_clicks / unique_opens
  bounce_rate           DECIMAL   -- total_bounces / total_sends
  target_segment        VARCHAR   -- 'Military','Freshman','Graduate','Campus',etc
  department_code       VARCHAR   -- 'SFS','Advising','Admissions','FA','Career',etc

---

### TABLE: email_assets
Email template definitions. One row per email asset.
Columns:
  asset_id              VARCHAR   -- primary key
  business_unit         ENUM
  name                  VARCHAR   -- full email name e.g. 'EM-SFS-UC-FAFSA-Available'
  subject_line          VARCHAR
  pre_header            VARCHAR
  department_code       VARCHAR   -- parsed from name: 'SFS','FA','Advising',etc
  sender_address        VARCHAR
  sender_name           VARCHAR
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
  entry_mode            VARCHAR   -- 'SingleEntryAcrossAllVersions','MultipleEntries'
  target_audience       VARCHAR   -- 'Military','Freshman','Graduate',etc
  department            VARCHAR   -- owning department
  academic_term         VARCHAR   -- e.g. '25FA'
  created_date          TIMESTAMP
  last_modified_date    TIMESTAMP

---

### TABLE: journey_activities
Individual steps within a journey. Each email/SMS send is one activity.
Columns:
  activity_id           VARCHAR
  journey_id            VARCHAR   -- FK → journeys.journey_id
  journey_name          VARCHAR
  business_unit         ENUM
  activity_name         VARCHAR
  activity_type         ENUM      -- 'EMAIL','SMS','WAIT','DECISIONSPLIT',etc
  email_id              VARCHAR   -- FK → email_assets.asset_id (null for SMS)
  email_name            VARCHAR
  email_subject         VARCHAR
  send_status           ENUM      -- 'Active','Stopped','Paused',etc
  sms_asset_id          VARCHAR   -- FK → sms_assets.asset_id (null for email)
  ga_campaign_name      VARCHAR
  last_modified_date    TIMESTAMP

---

### TABLE: automations
Scheduled automation definitions that feed journeys.
Columns:
  automation_id         VARCHAR   -- primary key (UUID)
  name                  VARCHAR
  business_unit         ENUM
  type                  VARCHAR   -- 'scheduled','triggered'
  status                ENUM      -- 'Active','Paused','Stopped','Scheduled','Building'
  schedule              VARCHAR   -- human readable, e.g. 'Daily 8:00AM'
  last_run_time         TIMESTAMP

---

### TABLE: journey_entry_sources
How journeys are triggered/populated.
Columns:
  entry_source_id       VARCHAR
  journey_id            VARCHAR   -- FK → journeys.journey_id
  entry_type            ENUM      -- 'AutomationAudience','EmailAudience','Schedule',etc
  data_extension_name   VARCHAR
  automation_id         VARCHAR   -- FK → automations.automation_id (if automation-driven)
  schedule_frequency    ENUM      -- 'Daily','Weekly','Monthly','Once'
  schedule_start_time   TIMESTAMP
  schedule_end_time     TIMESTAMP

---

### TABLE: subscribers
Student/contact records.
Columns:
  subscriber_key        VARCHAR   -- primary key
  business_unit         ENUM
  student_stage         ENUM      -- 'Inquiry','Applicant','Admitted','Enrolled','Alumni'
  student_type          ENUM      -- 'Military','International','Domestic','Transfer'
  student_level         ENUM      -- 'Freshman','Sophomore','Junior','Senior','Graduate','Doctoral'
  campus                VARCHAR
  level                 VARCHAR   -- 'UG' or 'GR'
  admit_term            VARCHAR   -- e.g. '25FA'
  is_active_subscriber  BOOLEAN

---

### TABLE: opportunities
Downstream funnel data -- what happened after students received emails.
Columns:
  subscriber_key        VARCHAR   -- FK → subscribers.subscriber_key
  stage_name            VARCHAR   -- 'Application','Admitted','Enrolled','Registered'
  program_name          VARCHAR
  program_level         VARCHAR   -- 'UG','GR'
  admit_term            VARCHAR
  enrolled_term         VARCHAR
  registered_next_term  BOOLEAN   -- did they register for next term?
  withdrew              BOOLEAN
  gpa                   DECIMAL

---

### TABLE: sms_assets
SMS message definitions.
Columns:
  asset_id, business_unit, name, message_text,
  keyword_id, short_code, created_time, last_modified_date

---

### TABLE: landing_page_assets
Landing page definitions.
Columns:
  asset_id, business_unit, name, page_name, page_url,
  published_status ('Published','Unpublished','Draft'),
  has_form, has_google_analytics, published_date,
  created_time, last_modified_date

---

### TABLE: content_block_assets
Reusable content blocks embedded in emails.
Columns:
  asset_id, business_unit, name, folder_name,
  copy_found, emails_found, created_time, last_modified_date

---

### TABLE: image_assets
Image metadata and historical performance when used in emails.
Columns:
  image_url, email_asset_id, image_type ('hero','banner','icon','cta','background'),
  subject_matter ('campus','student','graduation','financial','abstract','faculty'),
  primary_color, has_people, has_text_overlay,
  avg_click_rate, avg_open_rate, usage_count, business_unit

---

## KEY RELATIONSHIPS

  dod_metrics.email_asset_id    → email_assets.asset_id
  dod_metrics.journey_id        → journeys.journey_id
  journey_activities.journey_id → journeys.journey_id
  journey_activities.email_id   → email_assets.asset_id
  journey_entry_sources.journey_id   → journeys.journey_id
  journey_entry_sources.automation_id → automations.automation_id
  opportunities.subscriber_key  → subscribers.subscriber_key
  image_assets.email_asset_id   → email_assets.asset_id

---

## BUSINESS LOGIC RULES

1. "Active" journeys = journeys.status = 'Active'
2. "Automated" journeys = have a journey_entry_source with entry_type = 'AutomationAudience'
3. To get monthly performance: AVG(open_rate), AVG(click_rate), SUM(total_sends)
   grouped by DATE_TRUNC('month', send_date)
4. "Campus students" = subscribers.campus IN ('UC') or business_unit = 'UC'
5. "Military students" = subscribers.student_type = 'Military' or business_unit = 'MIL'
   or dod_metrics.target_segment = 'Military'
6. Rates are stored as decimals (0.35 = 35%). Multiply by 100 for percentage display.
7. "Lift" from SMS = compare click_rate or open_rate between journeys that have
   SMS activities vs those that do not, for the same audience segment.
8. YOY comparison: join on academic_terms and filter by season + year.
"""
