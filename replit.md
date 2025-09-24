# Football Visualizer

## Overview

Football Visualizer is a Django-based web application designed to analyze and visualize football match data. The application provides a dashboard interface where users can search for specific teams and view statistical insights through interactive charts. The system focuses on tracking match results, goals scored/conceded, and team performance over time, making it a valuable tool for football analytics and data visualization.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
The application is built on Django 5.2.6, following the standard Django project structure with a modular app-based architecture. The main project (`football_visualizer`) contains global settings and URL routing, while the `dashboard` app handles all football-related functionality.

### Data Model Design
The core data model centers around a `Match` entity that captures essential football match information:
- Match date, teams (home/away), goals scored, and match result
- Season tracking for temporal analysis
- Result classification (Home Win, Away Win, Draw) for quick statistical aggregation

### API Architecture
The application implements a hybrid approach combining traditional Django views with JSON API endpoints:
- **Template Views**: Serve the main dashboard interface using Django's template system
- **JSON API**: Provide team statistics data for frontend consumption
- **RESTful Design**: Team-specific endpoints follow `/team/<team_name>/` URL patterns

### Frontend Architecture
The frontend uses a server-side rendered approach with client-side JavaScript enhancement:
- Bootstrap 5.3.0 for responsive UI components and styling
- Chart.js for interactive data visualizations
- Vanilla JavaScript for API integration and dynamic content updates
- Progressive enhancement pattern where the base functionality works without JavaScript

### Data Management
The application includes a custom Django management command (`load_matches`) for data import:
- CSV file processing with flexible date parsing
- Bulk data operations with optional data clearing
- Error handling and validation during import process

### Administrative Interface
Django's built-in admin interface is customized for match data management:
- Enhanced list views with filtering and search capabilities
- Date-based hierarchical navigation
- Custom display fields for improved usability

## External Dependencies

### Core Framework Dependencies
- **Django 5.2.6**: Main web framework providing ORM, templating, and admin interface
- **python-decouple**: Environment variable management for configuration
- **dj-database-url**: Database URL parsing for deployment flexibility

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive design and UI components
- **Chart.js**: JavaScript charting library for data visualization

### Database Support
- **SQLite**: Default database for development (Django built-in)
- **PostgreSQL**: Production database support through dj-database-url configuration

### Development Tools
- **Django Management Commands**: Custom command system for data import operations
- **Django Migrations**: Database schema version control and deployment
- **Django Admin**: Built-in administrative interface for content management

The application is designed to be deployment-ready with configurable database backends and environment-based settings management, making it suitable for both development and production environments.