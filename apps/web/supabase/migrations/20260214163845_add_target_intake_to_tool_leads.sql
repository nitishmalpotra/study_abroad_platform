/*
  # Add target_intake column to tool_leads

  1. Modified Tables
    - `tool_leads`
      - Added `target_intake` (text) - The intake period the student is targeting (e.g., Fall 2026, Spring 2027)

  2. Notes
    - Column is nullable with empty string default to avoid breaking existing rows
*/

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'tool_leads' AND column_name = 'target_intake'
  ) THEN
    ALTER TABLE tool_leads ADD COLUMN target_intake text DEFAULT '';
  END IF;
END $$;
