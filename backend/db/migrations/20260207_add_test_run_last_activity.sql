ALTER TABLE test_runs ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMPTZ;

UPDATE test_runs
SET last_activity_at = COALESCE(last_activity_at, submitted_at, created_at)
WHERE last_activity_at IS NULL;

ALTER TABLE test_runs
  ALTER COLUMN last_activity_at SET NOT NULL,
  ALTER COLUMN last_activity_at SET DEFAULT now();

CREATE INDEX IF NOT EXISTS ix_test_runs_last_activity_at ON test_runs (last_activity_at);
