/*
  # Create tool_leads table

  1. New Tables
    - `tool_leads`
      - `id` (uuid, primary key)
      - `phone` (text, not null) - User's phone number
      - `email` (text, not null) - User's email address
      - `target_country` (text, not null) - Country the student is targeting
      - `target_college` (text) - College the student is targeting
      - `journey_stage` (text, not null) - Current stage in study abroad journey
      - `tool_name` (text, not null) - Which tool they accessed
      - `created_at` (timestamptz) - When the lead was created

  2. Security
    - Enable RLS on `tool_leads` table
    - Add insert policy for anonymous users (public lead capture form)
*/

CREATE TABLE IF NOT EXISTS tool_leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  phone text NOT NULL,
  email text NOT NULL,
  target_country text NOT NULL,
  target_college text DEFAULT '',
  journey_stage text NOT NULL,
  tool_name text NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE tool_leads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous lead submissions"
  ON tool_leads
  FOR INSERT
  TO anon
  WITH CHECK (
    char_length(phone) >= 10
    AND char_length(email) >= 5
    AND char_length(target_country) >= 1
    AND char_length(journey_stage) >= 1
    AND char_length(tool_name) >= 1
  );
