-- Script SQL pour créer la table notifications manuellement
-- Utilisation: psql -U votre_user -d votre_db -f create_notifications_table.sql

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    message TEXT,
    recipient VARCHAR(50),
    notification_type VARCHAR(20) DEFAULT 'sms',
    status VARCHAR(20) DEFAULT 'pending',
    twilio_sid VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Créer les index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_twilio_sid ON notifications(twilio_sid);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- Pour SQLite (si vous utilisez SQLite au lieu de PostgreSQL)
-- CREATE TABLE IF NOT EXISTS notifications (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     message TEXT,
--     recipient VARCHAR(50),
--     notification_type VARCHAR(20) DEFAULT 'sms',
--     status VARCHAR(20) DEFAULT 'pending',
--     twilio_sid VARCHAR(100),
--     error_message TEXT,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
--     sent_at DATETIME
-- );
-- CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient);
-- CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
-- CREATE INDEX IF NOT EXISTS idx_notifications_twilio_sid ON notifications(twilio_sid);
-- CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

