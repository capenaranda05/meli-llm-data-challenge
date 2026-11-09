# Local Development Setup

Step-by-step guide for setting up the Catalog Portfolio API service for local development.

## Prerequisites

Before starting, ensure you have the following installed:

- **Java JDK 17** or higher
- **Gradle 7.3** or higher (or use the wrapper)
- **MySQL 8.0** or higher
- **RetailFlow CLI** (latest version)
- **Git** for version control


  <i class="fas fa-download"></i> Download Setup Template


## Step 1: Clone Repository

```bash
# Using RetailFlow CLI (recommended)
retailflow get catalog-portfolio-api

cd catalog-portfolio-api
```

## Step 2: Build and Run

### Build the Project

```bash
# Clean and build
./gradlew clean build

# Run tests
./gradlew test

# Check code quality
./gradlew check
```

### Run the Service

```bash
# Run with development profile
./gradlew run -Denvironment=development

# Or run with specific configuration
java -jar build/libs/catalog-portfolio-api-1.0.0.jar --environment=development
```

## Development Workflow

### Code Structure

```
src/main/java/com/retailflow/catalog/brands/
├── controller/     # HTTP controllers
├── service/        # Business logic
├── dao/           # Data access objects
├── model/         # Data models
├── dto/           # Data transfer objects
├── config/        # Configuration classes
├── validator/     # Validation services
└── util/          # Utility classes
```

### Running Tests

```bash
# Run all tests
./gradlew test

# Run specific test class
./gradlew test --tests BrandServiceTest

# Run integration tests
./gradlew integrationTest
```

### Code Quality Checks

```bash
# PMD static analysis
./gradlew pmdMain

# Checkstyle
./gradlew checkstyle

# SpotBugs
./gradlew spotbugsMain
```

## IDE Configuration

### IntelliJ IDEA

1. Import project as Gradle project
2. Set Project SDK to Java 17
3. Configure code style:
   - Import `config/checkstyle/checkstyle-main.xml`
   - Set line separator to LF
   - Set encoding to UTF-8

### VS Code

Install recommended extensions:
- Java Extension Pack
- Gradle for Java
- MySQL

## Troubleshooting

### Common Issues

**Database Connection Error**
```
Solution: Check MySQL is running and credentials are correct
Command: sudo systemctl status mysql
```

**Port Already in Use**
```
Solution: Change port in application.properties or kill process
Command: lsof -ti:8080 | xargs kill -9
```

**Gradle Build Issues**
```
Solution: Clean and rebuild
Commands: 
./gradlew clean
./gradlew build --refresh-dependencies
```

### Useful Commands

```bash
# Check running processes
jps -v

# Monitor logs
tail -f logs/application.log

# Check database connections
mysql -u your_username -p -e "SHOW PROCESSLIST;"
```

## Next Steps

After successful setup:
1. [API Reference](../api-reference/) - Learn about available endpoints
2. [Brand Management](../brand-management/) - Understand brand operations
3. [Architecture](../architecture/) - Explore system design 