SELECT 'CREATE DATABASE gearshare_test'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'gearshare_test'
)\gexec
