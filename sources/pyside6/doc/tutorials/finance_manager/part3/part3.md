(tutorial_financemanager_partthree)=

# Finance Manager Tutorial - Part 3

In this part of the tutorial, we will extend our finance manager app to create a REST API using
[FastAPI] and [Uvicorn]. This will allow us to perform server-side operations and interact with the
SQLite database created in Part 2 using [SQLAlchemy].

[FastAPI] is a modern, fast (high-performance), web framework for building APIs with Python.
It is built on top of [ASGI (Asynchronous Server Gateway Interface)], which allows for efficient
handling of concurrent requests.

[Uvicorn] is a lightning-fast ASGI server implementation, using uvloop and httptools. It provides
a high-performance server for running FastAPI applications.


To download the complete source code for this tutorial, visit
{ref}`example_tutorials_finance_manager_part3`.

## Prerequisites

Before we begin, make sure you have [FastAPI] and [Uvicorn] installed within your
Python environment.

You can install them using pip:

```bash
pip install fastapi uvicorn
```

## Project Structure

The overall project structure in this part of the tutorial is much different from the previous
parts. We move the frontend part that uses PySide6 and QML to a separate directory called `Frontend`
and the backend part that uses FastAPI to create a REST API to the SQLite database to a directory
called `Backend`.

```
├── Backend
│   ├── database.py
│   ├── main.py
│   └── rest_api.py
├── Frontend
│   ├── Finance
│   │   ├── AddDialog.qml
│   │   ├── FinanceDelegate.qml
│   │   ├── FinancePieChart.qml
│   │   ├── FinanceView.qml
│   │   ├── Main.qml
│   │   └── qmldir
│   ├── financemodel.py
│   └── main.py
```

## Let's Get Started!

First, let's create the `Backend` directory and move the `database.py` from the
[previous part](tutorial_financemanager_parttwo) to the `Backend` directory.

### Backend Setup

### Setting Up FastAPI

Create a new Python file `rest_api.py` in the `Backend` directory and add the following code:

<details>
<summary class="prominent-summary">rest_api.py</summary>

```{literalinclude} ../../../../../../../../../examples/tutorials/finance_manager/part3/Backend/rest_api.py
---
language: python
caption: rest_api.py
linenos: true
---
```
</details>

In `rest_api.py`, we set up a FastAPI application to handle Create and Read operations for the
finance data. The file includes:

1. **FastAPI Application**: Initializes a FastAPI instance.
2. **Pydantic Models**: Defines `FinanceCreate` for input validation and creating new records
and `FinanceRead` for output formatting. `FinanceRead` includes additional configuration for
ORM models.
3. **Database Dependency**: Provides a `get_db` function to manage database sessions.
4. **Create Endpoint**: A POST endpoint `/finances/` to add new finance entries to the database.
5. **Read Endpoint**: A GET endpoint `/finances/` to retrieve finance entries from the database.

This setup allows the application to interact with the database, enabling the creation and retrieval
of finance records via RESTful API endpoints.

### Creating a main Python File for the Backend

Create a new Python file `main.py` in the `Backend` directory and add the following code:

<details>
<summary class="prominent-summary">main.py</summary>

```{literalinclude} ../../../../../../../../../examples/tutorials/finance_manager/part3/Backend/main.py
---
language: python
caption: main.py
linenos: true
---
```
</details>

In `main.py`, along with initializing the database we create a [Uvicorn] server instance to run the
FastAPI application. The server runs on 127.0.0.1 at port 8000 and reloads automatically when code
changes are detected.

### Frontend Setup

Then we move on to the frontend part of the application, and connect it to the FastAPI backend.
We will create a new directory `Frontend`. Move the folder `Finance` and the files `financemodel.py`
and `main.py` from the previous parts to the `Frontend` directory.

Most of the code remains the same as in the previous parts, with minor changes to connect to the
REST API.

### Updating the FinanceModel Class

The following changes (highlighted) are made to the `financemodel.py` file which removes
the database interaction code from Python and adds the REST API interaction code.

<details>
<summary class="prominent-summary">financemodel.py</summary>

```{literalinclude} ../../../../../../../../../examples/tutorials/finance_manager/part3/Frontend/financemodel.py
---
language: python
caption: financemodel.py
linenos: true
emphasize-lines: 45-55, 92-103
---
```
</details>

A new method `fetchAllData` is added to the `FinanceModel` class to fetch all the finance data from
the REST API. This method is called when the application starts to populate the model with the
existing finance data. Additionally, the `append` method is updated to send a POST request to the
REST API to add a new finance entry.

### Updating the Main Python File for the Frontend

Finally, we update the `main.py` file in the `Frontend` directory to remove the database
initialization code.

<details>
<summary class="prominent-summary">main.py</summary>

```{literalinclude} ../../../../../../../../../examples/tutorials/finance_manager/part3/Frontend/main.py
---
language: python
caption: main.py
linenos: true
---
```
</details>

The rest of the code and the QML files remains the same as in the previous parts of the tutorial.

### Running the Application

To run the application, first start the backend FastAPI server by executing the `main.py` file in
the `Backend` directory using Python:

```bash
python Backend/main.py
```

This will start the Uvicorn server running the FastAPI application on `http://127.0.0.1:8000`.

After starting the backend server, run the frontend application by executing the `main.py` file in
the `Frontend` directory using Python:

```bash
python Frontend/main.py
```

This will start the PySide6 application that connects to the FastAPI backend to display the finance
data.

## Deployment

### Deploying the Application

To deploy the application, follow the same steps as in the
[first part](tutorial_financemanager_partone) of the tutorial.

## Summary

At the end of this tutorial, you have extended the finance manager app to include a REST API using
FastAPI and Uvicorn. The backend application interacts with the SQLite database using SQLAlchemy
and provides endpoints to create and retrieve finance records. The frontend application connects to
the backend using the REST API to display the finance data.

If you want to extend the application further, you can add more features like updating and deleting
finance records, adding user authentication etc.

[FastAPI]: https://fastapi.tiangolo.com/
[Uvicorn]: https://www.uvicorn.org/
[PyDantic]: https://pydantic-docs.helpmanual.io/
[SQAlchemy]: https://www.sqlalchemy.org/
