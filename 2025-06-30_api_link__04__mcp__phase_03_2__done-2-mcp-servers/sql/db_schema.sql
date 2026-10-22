-- Table definition for API configurations
CREATE TABLE api_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE COMMENT 'Unique name for the API configuration',
    description TEXT COMMENT 'Detailed description of the API configuration',
    endpoint VARCHAR(2048) NOT NULL COMMENT 'The full URL endpoint for the API request',
    method VARCHAR(10) NOT NULL COMMENT 'HTTP method (e.g., GET, POST, PUT, DELETE)',
    headers JSON COMMENT 'JSON object storing request headers as key-value pairs',
    body_template TEXT COMMENT 'Template for the request body, can contain placeholders',
    params JSON COMMENT 'JSON object or string storing query parameters template',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp of creation',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp of last update'
) COMMENT 'Stores configurations for making HTTP REST API requests';

-- Example of how to insert data (optional, for reference)
-- INSERT INTO api_config (name, description, endpoint, method, headers, body_template, params)
-- VALUES (
--   'GetUserAPI',
--   'Fetches user details by ID',
--   'https://api.example.com/users/{userId}',
--   'GET',
--   '{\"Authorization\": \"Bearer YOUR_TOKEN\", \"Content-Type\": \"application/json\"}',
--   NULL, -- No body for GET typically
--   '{\"include_details\": \"true\"}'
-- );
