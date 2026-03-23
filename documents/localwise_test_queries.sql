-- =====================================================
-- LocalWise SQL Processing Test File
-- =====================================================
-- 
-- This SQL file tests the SQL file processing capabilities
-- added to LocalWise v1.0.0.
--
-- Author: LocalWise Team
-- Version: 1.0.0
-- =====================================================

-- Create database schema for LocalWise document tracking
CREATE SCHEMA IF NOT EXISTS localwise;

-- Table to track processed documents
CREATE TABLE localwise.processed_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size BIGINT,
    chunks_created INTEGER DEFAULT 0,
    processing_status VARCHAR(20) DEFAULT 'completed'
);

-- Table to store document statistics
CREATE TABLE localwise.document_stats (
    id SERIAL PRIMARY KEY,
    date_processed DATE DEFAULT CURRENT_DATE,
    total_files INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    file_types_processed JSONB,
    processing_duration_seconds INTEGER
);

-- Insert sample data for supported file types
INSERT INTO localwise.processed_documents 
(filename, file_path, file_type, file_size, chunks_created) 
VALUES 
    ('sample_report.pdf', '/documents/sample_report.pdf', 'PDF', 2048576, 15),
    ('data_export.csv', '/documents/data_export.csv', 'CSV', 1024000, 8),
    ('config.json', '/documents/config.json', 'JSON', 4096, 2),
    ('settings.yaml', '/documents/settings.yaml', 'YAML', 2048, 1),
    ('structure.xml', '/documents/structure.xml', 'XML', 8192, 3),
    ('readme.txt', '/documents/readme.txt', 'TXT', 1024, 1),
    ('document.rtf', '/documents/document.rtf', 'RTF', 16384, 4),
    ('report.docx', '/docs/report.docx', 'DOCX', 65536, 12),
    ('Application.java', '/docs/src/Application.java', 'Java', 8192, 5),
    ('main.py', '/docs/scripts/main.py', 'Python', 4096, 3),
    ('queries.sql', '/docs/database/queries.sql', 'SQL', 2048, 2),
    ('app.js', '/docs/web/app.js', 'JavaScript', 16384, 6),
    ('types.ts', '/docs/web/types.ts', 'TypeScript', 4096, 2),
    ('utils.cpp', '/docs/native/utils.cpp', 'CPP', 12288, 7),
    ('header.h', '/docs/native/header.h', 'C', 2048, 1),
    ('service.cs', '/docs/dotnet/service.cs', 'C#', 8192, 4),
    ('handler.go', '/docs/go/handler.go', 'Go', 4096, 3),
    ('controller.php', '/docs/php/controller.php', 'PHP', 6144, 4),
    ('model.rb', '/docs/ruby/model.rb', 'Ruby', 4096, 2),
    ('lib.rs', '/docs/rust/lib.rs', 'Rust', 8192, 5),
    ('index.html', '/docs/web/index.html', 'HTML', 4096, 2),
    ('styles.css', '/docs/web/styles.css', 'CSS', 2048, 1),
    ('guide.md', '/docs/guide.md', 'Markdown', 8192, 4);

-- Query to get file type statistics
SELECT 
    file_type,
    COUNT(*) as file_count,
    SUM(chunks_created) as total_chunks,
    AVG(file_size) as avg_file_size,
    SUM(file_size) as total_size
FROM localwise.processed_documents 
GROUP BY file_type 
ORDER BY file_count DESC;

-- Query to get processing summary
SELECT 
    COUNT(DISTINCT file_type) as unique_file_types,
    COUNT(*) as total_files,
    SUM(chunks_created) as total_chunks,
    SUM(file_size) as total_bytes
FROM localwise.processed_documents;

-- Query to find largest files by type
SELECT 
    file_type,
    filename,
    file_size,
    chunks_created,
    processed_at
FROM localwise.processed_documents 
WHERE file_size = (
    SELECT MAX(file_size) 
    FROM localwise.processed_documents pd2 
    WHERE pd2.file_type = localwise.processed_documents.file_type
)
ORDER BY file_size DESC;

-- Create indexes for performance
CREATE INDEX idx_processed_docs_type ON localwise.processed_documents(file_type);
CREATE INDEX idx_processed_docs_date ON localwise.processed_documents(processed_at);
CREATE INDEX idx_processed_docs_status ON localwise.processed_documents(processing_status);

-- Create view for easy access to file statistics
CREATE VIEW localwise.file_type_summary AS
SELECT 
    file_type,
    COUNT(*) as file_count,
    SUM(chunks_created) as total_chunks,
    ROUND(AVG(file_size)::numeric, 2) as avg_file_size_bytes,
    SUM(file_size) as total_size_bytes,
    MIN(processed_at) as first_processed,
    MAX(processed_at) as last_processed
FROM localwise.processed_documents 
GROUP BY file_type;

-- Sample query using the view
SELECT * FROM localwise.file_type_summary 
ORDER BY total_chunks DESC;

COMMIT;