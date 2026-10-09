"""Code templates for common use cases"""

from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# Common code templates organized by language and use case
CODE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "python": {
        "fastapi_endpoint": """from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI()


class {{request_model}}Request(BaseModel):
    {{request_fields}}


class {{response_model}}Response(BaseModel):
    {{response_fields}}


@app.post("/{{endpoint}}", response_model={{response_model}}Response)
async def {{function_name}}(
    request: {{request_model}}Request,
    # Add dependencies here
) -> {{response_model}}Response:
    '''{{description}}'''
    # Implement your endpoint logic here
    pass
""",
        
        "python_class": """class {{class_name}}:
    '''{{description}}'''
    
    def __init__(self, {{init_params}}):
        '''Initialize the {{class_name}} class.
        
        Args:
            {{init_args}}
        '''
        {{init_body}}
    
    def {{method_name}}(self, {{method_params}}) -> {{return_type}}:
        '''{{method_description}}
        
        Args:
            {{method_args}}
        
        Returns:
            {{return_description}}
        '''
        {{method_body}}
""",
        
        "python_function": """import {{imports}}


def {{function_name}}({{params}}) -> {{return_type}}:
    '''{{description}}
    
    Args:
        {{args}}
    
    Returns:
        {{return_description}}
    
    Raises:
        {{exceptions}}
    '''
    {{body}}
""",
        
        "python_script": """#!/usr/bin/env python3
"""{{description}}"""

import {{imports}}


def main({{args}}):
    '''Main function.'''
    {{body}}


if __name__ == "__main__":
    main()
""",
        
        "python_test": """import unittest
from {{module}} import {{class_or_function}}


class Test{{class_name}}(unittest.TestCase):
    '''Test cases for {{class_name}}.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        {{setup}}
    
    def test_{{test_case}}(self):
        '''Test {{test_description}}.'''
        {{test_body}}
    
    def tearDown(self):
        '''Clean up after tests.'''
        {{teardown}}


if __name__ == "__main__":
    unittest.main()
""",
    },
    
    "javascript": {
        "express_endpoint": """const express = require('express');
const router = express.Router();

/**
 * {{description}}
 * @route {{method}} /{{endpoint}}
 * @param {{{request_type}}} req - Request object
 * @param {{{response_type}}} res - Response object
 * @returns {{{return_type}}} - Response data
 */
router.{{method}}('/{{endpoint}}', async (req, res) => {
    try {
        // Implement your endpoint logic here
        {{body}}
    } catch (error) {
        console.error('Error in {{function_name}}:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
""",
        
        "javascript_class": """/**
 * {{description}}
 */
class {{class_name}} {
    /**
     * Create a {{class_name}} instance.
     * @param {Object} options - Configuration options
     * @param {{{params}}} options.{{param_names}} - Parameter descriptions
     */
    constructor({{params}}) {
        {{constructor_body}}
    }
    
    /**
     * {{method_description}}
     * @param {{{param_types}}} {{param_names}} - Parameter descriptions
     * @returns {{{return_type}}} - Return description
     */
    {{method_name}}({{params}}) {
        {{method_body}}
    }
}

module.exports = {{class_name}};
""",
        
        "javascript_function": """/**
 * {{description}}
 * @param {{{param_types}}} {{param_names}} - Parameter descriptions
 * @returns {{{return_type}}} - Return description
 * @throws {{{exceptions}}} - Exception descriptions
 */
function {{function_name}}({{params}}) {
    {{body}}
}

module.exports = { {{function_name}} };
""",
    },
    
    "typescript": {
        "fastapi_like_endpoint": """import { Router, Request, Response } from 'express';
import { {{request_type}}, {{response_type}} } from './types';

const router = Router();

/**
 * {{description}}
 */
router.{{method}}('/{{endpoint}}', async (req: Request<{{request_type}}>, res: Response<{{response_type}}>) => {
    try {
        {{body}}
    } catch (error) {
        console.error('Error in {{function_name}}:', error);
        res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' });
    }
});

export default router;
""",
        
        "typescript_class": """/**
 * {{description}}
 */
export class {{class_name}} {
    private {{private_fields}};
    
    /**
     * Create a {{class_name}} instance.
     * @param {{params}} - Configuration options
     */
    constructor({{params}}) {
        {{constructor_body}}
    }
    
    /**
     * {{method_description}}
     * @param {{params}} - Method parameters
     * @returns {{return_type}} - Return description
     */
    public {{method_name}}({{params}}): {{return_type}} {
        {{method_body}}
    }
}
""",
        
        "typescript_interface": """/**
 * {{description}}
 */
export interface {{interface_name}} {
    {{fields}}
}
""",
    },
    
    "java": {
        "spring_boot_controller": """package {{package}};

import org.springframework.web.bind.annotation.*;
import org.springframework.http.*;

/**
 * {{description}}
 */
@RestController
@RequestMapping("/api/{{base_path}}")
public class {{class_name}}Controller {
    
    /**
     * {{method_description}}
     * @param {{params}} - Request parameters
     * @return ResponseEntity<{{return_type}}>
     */
    @{{method_mapping}}("/{{path}}")
    public ResponseEntity<{{return_type}}> {{method_name}}({{params}}) {
        {{body}}
    }
}
""",
        
        "java_class": """package {{package}};

/**
 * {{description}}
 */
public class {{class_name}} {
    private {{private_fields}};
    
    /**
     * Constructor for {{class_name}}.
     * @param {{params}} - Constructor parameters
     */
    public {{class_name}}({{params}}) {
        {{constructor_body}}
    }
    
    /**
     * {{method_description}}
     * @param {{params}} - Method parameters
     * @return {{return_type}}
     */
    public {{return_type}} {{method_name}}({{params}}) {
        {{method_body}}
    }
}
""",
    },
    
    "go": {
        "http_handler": """package {{package}}

import (
    "net/http"
    "{{imports}}"
)

// {{struct_name}} represents the request/response structure
type {{struct_name}} struct {
    {{fields}}
}

// {{handler_name}} handles {{description}}
func {{handler_name}}(w http.ResponseWriter, r *http.Request) {
    {{body}}
}

func init() {
    http.HandleFunc("/{{path}}", {{handler_name}})
}
""",
        
        "go_struct": """package {{package}}

// {{struct_name}} represents {{description}}
type {{struct_name}} struct {
    {{fields}}
}

// New{{struct_name}} creates a new {{struct_name}} instance
func New{{struct_name}}({{params}}) *{{struct_name}} {
    return &{{struct_name}}{
        {{initialization}},
    }
}

// {{method_name}} does {{method_description}}
func (s *{{struct_name}}) {{method_name}}({{params}}) {{return_type}} {
    {{body}}
}
""",
    },
    
    "rust": {
        "actix_web_handler": """use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};

/// {{description}}
#[derive(Debug, Serialize, Deserialize)]
pub struct {{struct_name}} {
    {{fields}}
}

/// {{handler_name}} - {{description}}
pub async fn {{handler_name}}(
    {{params}}: web::{{param_types}},
) -> impl Responder {
    {{body}}
}

pub fn configure(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::resource("/{{path}}")
            .route(web::{{method}}, {{handler_name}})
    );
}
""",
        
        "rust_struct": """/// {{description}}
#[derive(Debug, Clone)]
pub struct {{struct_name}} {
    {{fields}}
}

impl {{struct_name}} {
    /// Creates a new {{struct_name}} instance
    pub fn new({{params}}) -> Self {
        Self {
            {{initialization}},
        }
    }
    
    /// {{method_description}}
    pub fn {{method_name}}(&self, {{params}}) -> {{return_type}} {
        {{body}}
    }
}
""",
    },
    
    "sql": {
        "create_table": """-- {{description}}
CREATE TABLE {{table_name}} (
    {{columns}}
);

-- Create indexes
{{indexes}}

-- Create constraints
{{constraints}}
""",
        
        "select_query": """-- {{description}}
SELECT
    {{columns}}
FROM
    {{table_name}}
{{joins}}
WHERE
    {{conditions}}
GROUP BY
    {{group_by}}
ORDER BY
    {{order_by}}
LIMIT {{limit}};
""",
        
        "insert_query": """-- {{description}}
INSERT INTO {{table_name}} ({{columns}})
VALUES ({{values}});
""",
        
        "update_query": """-- {{description}}
UPDATE {{table_name}}
SET {{set_clause}}
WHERE {{conditions}};
""",
        
        "delete_query": """-- {{description}}
DELETE FROM {{table_name}}
WHERE {{conditions}};
""",
    },
    
    "html": {
        "html_page": """<!DOCTYPE html>
<html lang="{{lang}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        {{styles}}
    </style>
</head>
<body>
    <header>
        <h1>{{title}}</h1>
        <nav>
            {{navigation}}
        </nav>
    </header>
    
    <main>
        {{content}}
    </main>
    
    <footer>
        {{footer}}
    </footer>
    
    <script>
        {{scripts}}
    </script>
</body>
</html>
""",
        
        "react_component": """import React, { useState, useEffect } from 'react';
import './{{style_file}}';

/**
 * {{description}}
 */
export function {{component_name}}({{props}}) {
    const [{{state}}, set{{State}}] = useState({{initial_state}});
    
    useEffect(() => {
        {{effect_body}}
    }, [{{dependencies}}]);
    
    return (
        <div className="{{component_name}}">
            {{jsx_body}}
        </div>
    );
}

export default {{component_name}};
""",
    },
    
    "docker": {
        "dockerfile": """# {{description}}
# Use official base image
FROM {{base_image}}:{{tag}}

# Set environment variables
ENV {{env_vars}}

# Install dependencies
RUN {{install_commands}}

# Copy application files
COPY {{copy_commands}}

# Set working directory
WORKDIR {{workdir}}

# Expose ports
EXPOSE {{ports}}

# Set entrypoint
ENTRYPOINT ["{{entrypoint}}"]
CMD ["{{cmd}}"]
""",
        
        "docker_compose": """version: '{{version}}'

services:
  {{service_name}}:
    image: {{image}}
    container_name: {{container_name}}
    restart: {{restart_policy}}
    ports:
      - "{{host_port}}:{{container_port}}"
    volumes:
      - {{volumes}}
    environment:
      - {{env_vars}}
    depends_on:
      - {{dependencies}}
    networks:
      - {{network}}

networks:
  {{network}}:
    driver: bridge
""",
    },
    
    "yaml": {
        "api_spec": """openapi: 3.0.0
info:
  title: {{api_name}}
  description: {{description}}
  version: {{version}}

servers:
  - url: {{base_url}}
    description: {{server_description}}

paths:
  /{{path}}:
    {{method}}:
      summary: {{summary}}
      description: {{description}}
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/{{request_schema}}'
      responses:
        '200':
          description: {{response_description}}
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/{{response_schema}}'

components:
  schemas:
    {{schemas}}
""",
        
        "config_file": """# {{description}}
{{key}}: {{value}}
""",
    },
    
    "bash": {
        "script": """#!/bin/bash
# {{description}}

set -euo pipefail

# Define variables
{{variables}}

# Define functions
{{functions}}

# Main execution
main() {
    {{body}}
}

# Run main function
main "$@"
""",
        
        "cron_job": """# {{description}}
# Run {{schedule}}

{{command}}
""",
    },
}


class CodeTemplateManager:
    """Manages code templates"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir
        self._templates: Dict[str, Dict[str, str]] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load templates from built-in and directory"""
        # Load built-in templates
        self._templates = CODE_TEMPLATES.copy()
        
        # Load from directory if specified
        if self.template_dir and self.template_dir.exists():
            self._load_directory_templates()
    
    def _load_directory_templates(self) -> None:
        """Load templates from directory"""
        for lang_dir in self.template_dir.iterdir():
            if lang_dir.is_dir():
                language = lang_dir.name
                if language not in self._templates:
                    self._templates[language] = {}
                
                for template_file in lang_dir.glob("*.template"):
                    template_name = template_file.stem
                    template_content = template_file.read_text()
                    self._templates[language][template_name] = template_content
    
    def get_template(self, language: str, template_name: str) -> Optional[str]:
        """Get a template by language and name"""
        if language in self._templates:
            return self._templates[language].get(template_name)
        return None
    
    def get_templates_by_language(self, language: str) -> Dict[str, str]:
        """Get all templates for a language"""
        return self._templates.get(language, {})
    
    def list_languages(self) -> List[str]:
        """List all available languages"""
        return list(self._templates.keys())
    
    def list_templates(self, language: Optional[str] = None) -> Dict[str, List[str]]:
        """List all templates, optionally filtered by language"""
        if language:
            templates = self.get_templates_by_language(language)
            return {language: list(templates.keys())}
        
        return {lang: list(templates.keys()) for lang, templates in self._templates.items()}
    
    def render_template(
        self,
        language: str,
        template_name: str,
        variables: Dict[str, str]
    ) -> str:
        """Render a template with variables"""
        template = self.get_template(language, template_name)
        if not template:
            raise ValueError(f"Template {template_name} for language {language} not found")
        
        # Replace variables
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, value)
        
        return result
    
    def add_template(self, language: str, template_name: str, template_content: str) -> None:
        """Add a new template"""
        if language not in self._templates:
            self._templates[language] = {}
        
        self._templates[language][template_name] = template_content
        
        # Save to directory if configured
        if self.template_dir:
            self._save_template_to_directory(language, template_name, template_content)
    
    def _save_template_to_directory(self, language: str, template_name: str, content: str) -> None:
        """Save a template to the directory"""
        lang_dir = self.template_dir / language
        lang_dir.mkdir(exist_ok=True)
        
        template_file = lang_dir / f"{template_name}.template"
        template_file.write_text(content)


# Global template manager instance
_template_manager: Optional[CodeTemplateManager] = None


def get_template_manager() -> CodeTemplateManager:
    """Get the global template manager instance"""
    global _template_manager
    if _template_manager is None:
        from open_coordinator.config.settings import get_settings
        settings = get_settings()
        _template_manager = CodeTemplateManager(settings.templates.template_dir)
    return _template_manager
