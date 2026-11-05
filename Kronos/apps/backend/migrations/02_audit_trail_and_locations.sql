-- Create locations table for multisede support
CREATE TABLE IF NOT EXISTS locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    radius_meters INTEGER DEFAULT 500 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS for locations
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone logged in can view locations
CREATE POLICY "Users can view locations" ON locations
    FOR SELECT USING (auth.role() = 'authenticated');

-- Insert default office coordinates (Madrid Sol office example)
INSERT INTO locations (name, latitude, longitude, radius_meters)
VALUES ('Oficina Principal - Madrid Sol', 40.4168, -3.7038, 500)
ON CONFLICT DO NOTHING;

-- Create time_entries_audit table for audit logs
CREATE TABLE IF NOT EXISTS time_entries_audit (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entry_id UUID NOT NULL,
    old_type TEXT,
    new_type TEXT,
    old_recorded_at TIMESTAMPTZ,
    new_recorded_at TIMESTAMPTZ,
    changed_by UUID,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS for time_entries_audit
ALTER TABLE time_entries_audit ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own audit records
CREATE POLICY "Users can view own audits" ON time_entries_audit
    FOR SELECT USING (auth.uid() = changed_by);

-- Trigger function to prevent deletes and audit updates
CREATE OR REPLACE FUNCTION audit_time_entries_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Normativa Laboral 2025: No está permitido eliminar registros de fichaje de jornada laboral.';
    ELSIF TG_OP = 'UPDATE' THEN
        -- Prevent changing the user_id or id of the entry
        IF OLD.user_id <> NEW.user_id THEN
            RAISE EXCEPTION 'No se permite reasignar el registro de jornada a otro empleado.';
        END IF;

        -- Insert audit trail record
        INSERT INTO time_entries_audit (
            entry_id,
            old_type,
            new_type,
            old_recorded_at,
            new_recorded_at,
            changed_by
        ) VALUES (
            OLD.id,
            OLD.type::text,
            NEW.type::text,
            OLD.recorded_at,
            NEW.recorded_at,
            auth.uid()
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to time_entries
DROP TRIGGER IF EXISTS trg_audit_time_entries ON time_entries;
CREATE TRIGGER trg_audit_time_entries
BEFORE UPDATE OR DELETE ON time_entries
FOR EACH ROW
EXECUTE FUNCTION audit_time_entries_changes();
