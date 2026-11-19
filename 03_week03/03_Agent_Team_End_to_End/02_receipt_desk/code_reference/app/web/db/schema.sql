BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS clients (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE,
    name text NOT NULL,
    business_type text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    display_name text NOT NULL,
    role text NOT NULL CHECK (role IN ('staff', 'lead', 'owner', 'client')),
    client_id uuid REFERENCES clients (id),
    CHECK ((role = 'client') = (client_id IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS sessions (
    token text PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    expires_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS batches (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id uuid NOT NULL REFERENCES clients (id),
    uploaded_by uuid NOT NULL REFERENCES users (id),
    priority text NOT NULL DEFAULT 'normal' CHECK (priority IN ('normal', 'urgent')),
    urgent_set_by uuid REFERENCES users (id),
    urgent_set_at timestamptz,
    receipt_count integer NOT NULL CHECK (receipt_count > 0),
    accepted_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, client_id)
);

CREATE TABLE IF NOT EXISTS receipts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id uuid NOT NULL,
    client_id uuid NOT NULL REFERENCES clients (id),
    file_name text NOT NULL,
    file_path text NOT NULL,
    mime_type text NOT NULL,
    size_bytes integer NOT NULL CHECK (size_bytes >= 0),
    status text NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'review', 'confirmed', 'unreadable')),
    dispatch_state text NOT NULL DEFAULT 'pending'
        CHECK (dispatch_state IN ('pending', 'sent', 'hold')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    ai_merchant text,
    ai_receipt_date date,
    ai_total numeric(12,2),
    total_confidence numeric CHECK (total_confidence BETWEEN 0 AND 1),
    merchant text,
    receipt_date date,
    total numeric(12,2),
    flag_low_confidence boolean NOT NULL DEFAULT false,
    flag_mismatch boolean NOT NULL DEFAULT false,
    entered_manually boolean NOT NULL DEFAULT false,
    category_id uuid REFERENCES categories (id),
    accepted_at timestamptz NOT NULL DEFAULT now(),
    result_at timestamptz,
    review_opened_at timestamptz,
    review_seconds integer,
    confirmed_by uuid REFERENCES users (id),
    confirmed_at timestamptz,
    unreadable_reason text,
    FOREIGN KEY (batch_id, client_id) REFERENCES batches (id, client_id)
);

CREATE TABLE IF NOT EXISTS receipt_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id uuid NOT NULL REFERENCES receipts (id) ON DELETE CASCADE,
    line_no integer NOT NULL CHECK (line_no > 0),
    ai_name text,
    ai_price numeric(12,2),
    name text,
    price numeric(12,2),
    removed boolean NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS receipt_edits (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id uuid NOT NULL REFERENCES receipts (id) ON DELETE CASCADE,
    field text NOT NULL,
    old_value text,
    new_value text,
    edited_by uuid NOT NULL REFERENCES users (id),
    edited_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS receipt_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id uuid NOT NULL REFERENCES receipts (id) ON DELETE CASCADE,
    from_status text CHECK (from_status IN ('queued', 'processing', 'review', 'confirmed', 'unreadable')),
    to_status text NOT NULL CHECK (to_status IN ('queued', 'processing', 'review', 'confirmed', 'unreadable')),
    actor_id uuid REFERENCES users (id),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gpu_benchmarks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    gpu_count integer NOT NULL,
    receipt_count integer NOT NULL,
    seconds numeric NOT NULL,
    cost_baht numeric(12,2) NOT NULL,
    measured_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS system_state (
    key text PRIMARY KEY,
    value text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS sessions_expires_at_idx ON sessions (expires_at);
CREATE INDEX IF NOT EXISTS batches_urgent_set_at_idx ON batches (urgent_set_at) WHERE priority = 'urgent';
CREATE INDEX IF NOT EXISTS receipts_batch_id_idx ON receipts (batch_id);
CREATE INDEX IF NOT EXISTS receipts_dispatch_idx ON receipts (dispatch_state, accepted_at)
    WHERE status IN ('queued', 'processing');
CREATE INDEX IF NOT EXISTS receipts_client_date_idx ON receipts (client_id, receipt_date)
    WHERE status = 'confirmed';
CREATE INDEX IF NOT EXISTS receipt_items_receipt_id_idx ON receipt_items (receipt_id, line_no);
CREATE INDEX IF NOT EXISTS receipt_edits_receipt_id_idx ON receipt_edits (receipt_id, edited_at);
CREATE INDEX IF NOT EXISTS receipt_events_receipt_id_idx ON receipt_events (receipt_id, created_at);

-- The HTTP handler checks ENABLE_TEST_RESET and X-Test-Token before passing
-- the server-side enable flag here. Schema installation never loads fixtures.
CREATE OR REPLACE FUNCTION reset_test_data(
    options jsonb DEFAULT '{}'::jsonb,
    enable_test_reset text DEFAULT NULL
) RETURNS jsonb
LANGUAGE plpgsql
AS $reset$
DECLARE
    option_name text;
    pending_normal integer;
    urgent_today integer;
    urgent_yesterday integer;
    workers_alive integer;
    include_overdue boolean;
    reset_at timestamptz;
    yesterday_2359 timestamptz;
    first_client_id uuid;
    staff_id uuid;
    lead_id uuid;
BEGIN
    IF enable_test_reset IS DISTINCT FROM '1' THEN
        RAISE EXCEPTION 'Test reset is disabled' USING ERRCODE = '42501';
    END IF;

    IF jsonb_typeof(options) IS DISTINCT FROM 'object' THEN
        RAISE EXCEPTION 'Reset options must be a JSON object' USING ERRCODE = '22023';
    END IF;

    FOREACH option_name IN ARRAY ARRAY['pendingNormal', 'urgentToday', 'urgentYesterday', 'workersAlive']
    LOOP
        IF options ? option_name AND (
            jsonb_typeof(options -> option_name) <> 'number'
            OR options ->> option_name !~ '^[0-9]+$'
        ) THEN
            RAISE EXCEPTION '% must be a non-negative integer', option_name USING ERRCODE = '22023';
        END IF;
    END LOOP;
    IF options ? 'overdue' AND jsonb_typeof(options -> 'overdue') <> 'boolean' THEN
        RAISE EXCEPTION 'overdue must be a boolean' USING ERRCODE = '22023';
    END IF;

    pending_normal := coalesce((options ->> 'pendingNormal')::integer, 0);
    urgent_today := coalesce((options ->> 'urgentToday')::integer, 0);
    urgent_yesterday := coalesce((options ->> 'urgentYesterday')::integer, 0);
    workers_alive := coalesce((options ->> 'workersAlive')::integer, 2);
    include_overdue := coalesce((options ->> 'overdue')::boolean, false);

    TRUNCATE TABLE receipt_events, receipt_edits, receipt_items, receipts, batches,
        sessions, users, categories, clients, gpu_benchmarks, system_state;

    reset_at := clock_timestamp();
    yesterday_2359 := (
        date_trunc('day', reset_at AT TIME ZONE 'Asia/Bangkok') - interval '1 minute'
    ) AT TIME ZONE 'Asia/Bangkok';

    INSERT INTO clients (code, name, business_type) VALUES
        ('CL-01', 'ร้านข้าวแกงสมชาย', 'ร้านอาหาร'),
        ('CL-02', 'ร้านกาแฟมะลิ', 'ร้านกาแฟ'),
        ('CL-03', 'ร้านวัสดุทวีทรัพย์', 'วัสดุก่อสร้าง');

    INSERT INTO users (email, password_hash, display_name, role, client_id)
    SELECT fixture.email, crypt('receiptdesk-test', gen_salt('bf', 10)),
           fixture.display_name, fixture.role, clients.id
    FROM (VALUES
        ('pim@receiptdesk.test', 'คุณพิมพ์', 'staff', NULL),
        ('nan@receiptdesk.test', 'คุณแนน', 'staff', NULL),
        ('kitti@receiptdesk.test', 'คุณกิตติ', 'lead', NULL),
        ('orathai@receiptdesk.test', 'คุณอรทัย', 'owner', NULL),
        ('somchai@receiptdesk.test', 'คุณสมชาย', 'client', 'CL-01'),
        ('malee@receiptdesk.test', 'คุณมาลี', 'client', 'CL-02')
    ) AS fixture(email, display_name, role, client_code)
    LEFT JOIN clients ON clients.code = fixture.client_code;

    INSERT INTO categories (name) VALUES
        ('วัตถุดิบ'), ('ค่าแก๊ส'), ('ค่าน้ำแข็ง'), ('อื่น ๆ');

    SELECT id INTO STRICT first_client_id FROM clients WHERE code = 'CL-01';
    SELECT id INTO STRICT staff_id FROM users WHERE email = 'pim@receiptdesk.test';
    SELECT id INTO STRICT lead_id FROM users WHERE email = 'kitti@receiptdesk.test';

    WITH fixtures(code, client_code, receipt_day, uploaded_local, total, category, confirmer) AS (
        VALUES
            ('S-01', 'CL-01', DATE '2026-10-31', TIMESTAMP '2026-10-31 18:00', 150.00, 'วัตถุดิบ', 'pim@receiptdesk.test'),
            ('S-02', 'CL-01', DATE '2026-11-01', TIMESTAMP '2026-11-01 00:30', 200.50, 'วัตถุดิบ', 'pim@receiptdesk.test'),
            ('S-03', 'CL-01', DATE '2026-11-02', TIMESTAMP '2026-11-02 09:00', 99.50, 'ค่าน้ำแข็ง', 'pim@receiptdesk.test'),
            ('S-04', 'CL-01', DATE '2026-11-30', TIMESTAMP '2026-11-30 23:50', 1000.00, 'วัตถุดิบ', 'nan@receiptdesk.test'),
            ('S-05', 'CL-01', DATE '2026-12-01', TIMESTAMP '2026-12-01 08:00', 75.25, 'ค่าแก๊ส', 'nan@receiptdesk.test'),
            ('S-06', 'CL-01', DATE '2026-11-15', TIMESTAMP '2026-11-15 10:00', 500.00, NULL, NULL),
            ('S-07', 'CL-01', DATE '2026-11-10', TIMESTAMP '2026-12-02 11:00', 40.00, 'ค่าแก๊ส', 'pim@receiptdesk.test'),
            ('S-08', 'CL-02', DATE '2026-11-05', TIMESTAMP '2026-11-05 14:00', 999.00, 'วัตถุดิบ', 'nan@receiptdesk.test')
    ), base AS MATERIALIZED (
        SELECT fixtures.*, gen_random_uuid() AS batch_id, clients.id AS client_id,
               categories.id AS category_id, users.id AS confirmed_by,
               uploaded_local AT TIME ZONE 'Asia/Bangkok' AS accepted_at
        FROM fixtures
        JOIN clients ON clients.code = fixtures.client_code
        LEFT JOIN categories ON categories.name = fixtures.category
        LEFT JOIN users ON users.email = fixtures.confirmer
    ), loaded_batches AS (
        INSERT INTO batches (id, client_id, uploaded_by, receipt_count, accepted_at)
        SELECT batch_id, client_id, coalesce(confirmed_by, staff_id), 1, accepted_at
        FROM base
        RETURNING id
    ), loaded_receipts AS (
        INSERT INTO receipts (
            batch_id, client_id, file_name, file_path, mime_type, size_bytes,
            status, dispatch_state, attempts, ai_merchant, ai_receipt_date, ai_total,
            total_confidence, merchant, receipt_date, total,
            category_id, accepted_at, result_at, confirmed_by, confirmed_at
        )
        SELECT batch_id, client_id, code || '.jpg', 'fixtures/' || code || '.jpg', 'image/jpeg', 0,
               CASE WHEN confirmed_by IS NULL THEN 'review' ELSE 'confirmed' END,
               'hold', 1, 'ร้านตัวอย่าง', receipt_day, total, 0.99, 'ร้านตัวอย่าง', receipt_day, total,
               category_id, accepted_at, accepted_at + interval '1 minute', confirmed_by,
               CASE WHEN confirmed_by IS NOT NULL THEN accepted_at + interval '2 minutes' END
        FROM base
        JOIN loaded_batches ON loaded_batches.id = base.batch_id
        RETURNING id, total
    )
    INSERT INTO receipt_items (receipt_id, line_no, ai_name, ai_price, name, price)
    SELECT id, 1, 'รายการตัวอย่าง', total, 'รายการตัวอย่าง', total
    FROM loaded_receipts;

    WITH reset_batches AS MATERIALIZED (
        SELECT gen_random_uuid() AS id, 'pending-' || offset_no AS stem,
               'normal' AS priority, least(100::bigint, pending_normal - offset_no)::integer AS receipt_count,
               reset_at AS accepted_at, NULL::timestamptz AS urgent_set_at, NULL::timestamptz AS result_at
        FROM generate_series(0::bigint, pending_normal::bigint - 1, 100) AS offsets(offset_no)
        UNION ALL
        SELECT gen_random_uuid(), 'urgent-today-' || n, 'urgent', 1, reset_at, reset_at, NULL
        FROM generate_series(1, urgent_today) AS counts(n)
        UNION ALL
        SELECT gen_random_uuid(), 'urgent-yesterday-' || n, 'urgent', 1, yesterday_2359, yesterday_2359, NULL
        FROM generate_series(1, urgent_yesterday) AS counts(n)
        UNION ALL
        SELECT gen_random_uuid(), stem, 'normal', 1, reset_at - make_interval(mins => age),
               NULL,
               CASE WHEN has_result THEN reset_at - make_interval(mins => age - 30) END
        FROM (VALUES
            ('TD-BR13-a', 119, false),
            ('TD-BR13-b', 120, false),
            ('TD-BR13-c', 121, false),
            ('TD-BR13-d', 121, true)
        ) AS cases(stem, age, has_result)
        WHERE include_overdue
    ), loaded_batches AS (
        INSERT INTO batches (id, client_id, uploaded_by, priority, urgent_set_by, urgent_set_at,
                             receipt_count, accepted_at)
        SELECT id, first_client_id, staff_id, priority,
               CASE WHEN priority = 'urgent' THEN lead_id END,
               urgent_set_at, receipt_count, accepted_at
        FROM reset_batches
        RETURNING id
    )
    INSERT INTO receipts (batch_id, client_id, file_name, file_path, mime_type, size_bytes,
                          status, dispatch_state, accepted_at, result_at)
    SELECT reset_batches.id, first_client_id, filename, 'fixtures/' || filename, 'image/jpeg', 0,
           CASE WHEN result_at IS NULL THEN 'queued' ELSE 'review' END, 'hold', accepted_at, result_at
    FROM reset_batches
    JOIN loaded_batches ON loaded_batches.id = reset_batches.id
    CROSS JOIN LATERAL generate_series(1, receipt_count) AS lines(line_no)
    CROSS JOIN LATERAL (
        SELECT stem || CASE WHEN receipt_count > 1 THEN '-' || line_no ELSE '' END || '.jpg' AS filename
    ) AS files;

    INSERT INTO receipt_events (receipt_id, from_status, to_status, actor_id, created_at)
    SELECT receipts.id, event.from_status, event.to_status, event.actor_id, event.created_at
    FROM receipts
    JOIN batches ON batches.id = receipts.batch_id
    CROSS JOIN LATERAL (VALUES
        (NULL, 'queued', batches.uploaded_by, receipts.accepted_at),
        ('queued', 'processing', NULL, receipts.result_at - interval '1 second'),
        ('processing', 'review', NULL, receipts.result_at),
        ('review', 'confirmed', receipts.confirmed_by, receipts.confirmed_at)
    ) AS event(from_status, to_status, actor_id, created_at)
    WHERE event.created_at IS NOT NULL;

    INSERT INTO system_state (key, value, updated_at)
    VALUES ('workers_alive', workers_alive::text, reset_at);

    RETURN jsonb_build_object('ok', true, 'counts', jsonb_build_object(
        'users', (SELECT count(*) FROM users),
        'clients', (SELECT count(*) FROM clients),
        'receipts', (SELECT count(*) FROM receipts)
    ));
END;
$reset$;

COMMIT;
