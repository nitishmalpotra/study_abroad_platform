/*
  # Add target_course column to tool_leads

  1. Modified Tables
    - `tool_leads`
      - Added `target_course` (text) - The course or program the student is targeting (e.g., MS Computer Science, MBA)

  2. Notes
    - Column is nullable with empty string default to avoid breaking existing rows
*/

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'tool_leads' AND column_name = 'target_course'
  ) THEN
    ALTER TABLE tool_leads ADD COLUMN target_course text DEFAULT '';
  END IF;
END $$;