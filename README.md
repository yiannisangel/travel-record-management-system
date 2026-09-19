# Travel Record Management System

## Project Overview

This group project is to design and implement a record management system for a specialist travel agent.

The system manages three types of records:

1. **Client records**
2. **Flight records**
3. **Airline Company records**

The system allows the user, through a Graphical User Interface (GUI), to:

1. Create a record
2. Delete a record
3. Update a record
4. Search for and display records

The application uses a **list of dictionaries** as its internal record representation. Records are persisted locally using JSON files so that data can be reloaded when the application is restarted.

Information relating to the design of each module, design decisions, and testing is available in the [`docs`](docs/) folder in this repository.

---
## Team Members

| Team Member | Role |
|---|---|
| **Reem Ajishi** | GUI/UX Designer |
| **Ioannis Angelikas** | Project Manager |
| **Rodrigo de Almeida Barreto** | Programmer |
| **Gielen Rojas Lopez** | Tester |

---

## System Structure

The application is organised into separate modules to support separation of concerns:

- **`gui.py`** – presentation layer and user interaction
- **`controller.py`** – coordinates application behaviour and CRUD operations
- **`validation.py`** – input and business-rule validation
- **`storage.py`** – JSON persistence and record storage operations

The main application code is located in:

```text
RMS_project/