CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE widgets (
    id UUID PRIMARY KEY DEFAULT get_random_uuid(),
    owner_id UUID NOT NULL,
    widget_type TEXT NOT NULL CHECK (widget_type IN ('signup_form', 'cta_popover')),
    title TEXT NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    -- no default, API must always supply it
    button_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
)

CREATE INDEX idx_widgets_owner_id ON widgets (owner_id);