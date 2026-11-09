# Setup & Installation

Complete guide for setting up the Catalog Portfolio API service for local development and deployment.

## Overview

This section covers everything you need to get the Catalog Portfolio API service running locally, from prerequisites to database configuration.

**Available Items:**

- [Local Development](local-development.md) - Step-by-step local setup guide

## Quick Start

For experienced developers who want to get started quickly:


  <i class="fas fa-download"></i> Download Quick Start Template


```bash
# Clone the repository
retailflow get catalog-portfolio-api

# Navigate to project
cd catalog-portfolio-api

# Setup dependencies
./gradlew build

# Configure database
# See Database Setup section for details

# Run the service
./gradlew run
```

## Prerequisites Summary

- **Java**: JDK 17 or higher
- **Gradle**: 7.3 or higher  
- **MySQL**: 8.0 or higher
- **RetailFlow CLI**: Latest version
- **Git**: For version control

## Next Steps

After completing the setup, proceed to:
- [Architecture Overview](../architecture/) - Understand the system design
- [API Reference](../api-reference/) - Start using the API endpoints
- [Brand Management](../brand-management/) - Learn about brand operations 