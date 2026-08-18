CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL,
    widget_type TEXT NOT NULL CHECK (widget_type IN ('signup_form', 'cta_popover')),
    title TEXT NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    -- no default, API must always supply it
    button_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_widgets_owner_id ON widgets (owner_id);


CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    widget_id UUID NOT NULL REFERENCES widgets(id),
    data JSONB NOT NULL,
    ip_address INET,
    country TEXT,
    city TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_submissions_widget_id ON submissions (widget_id);