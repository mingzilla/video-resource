# Web Server & Framework Architecture

0. Core Concepts Overview
1. a) Web Servers vs App Frameworks
2. b) Protocol Specifications
3. c) HTML Serving Capability
4. Gunicorn + Uvicorn Workers Architecture
5. a) Deployment Combinations
6. b) Server-Framework Compatibility
7. c) Decision Matrix - Performance is Important!

## Core Concepts Overview

```
Web Architecture Stack:
[Client] ── [Web Server] ── [Protocol] ── [App Framework] ── [Your Code]
```

## 1. Web Servers vs App Frameworks

| Category           | Component                  | Purpose                        | Protocol Support |
|--------------------|----------------------------|--------------------------------|------------------|
| **Web Servers**    | Uvicorn                    | ASGI server for async apps     | ASGI only        |
|                    | Gunicorn                   | WSGI server for sync apps      | WSGI (default)   |
|                    | Gunicorn + Uvicorn Workers | Production ASGI deployment     | ASGI via workers |
| **App Frameworks** | FastAPI                    | Modern async API framework     | ASGI always      |
|                    | Flask                      | Traditional sync web framework | WSGI only        |
|                    | Django (WSGI mode)         | Traditional sync web framework | WSGI             |
|                    | Django (ASGI mode)         | Modern async web framework     | ASGI             |

## 2. Protocol Specifications

| Protocol | Interface Type | Characteristics                   | Use Cases                                         |
|----------|----------------|-----------------------------------|---------------------------------------------------|
| **WSGI** | Synchronous    | One request per thread            | Traditional web apps, simple APIs                 |
| **ASGI** | Asynchronous   | Event-driven, concurrent requests | Real-time apps, WebSockets, high-performance APIs |

### Protocol Compatibility Matrix

| Framework   | WSGI Support | ASGI Support | Default Protocol   |
|-------------|--------------|--------------|--------------------|
| **FastAPI** | ❌ No         | ✅ Yes        | ASGI               |
| **Flask**   | ✅ Yes        | ❌ No         | WSGI               |
| **Django**  | ✅ Yes        | ✅ Yes (3.0+) | WSGI (traditional) |

## 3. HTML Serving Capability

**Important**: Both protocols can serve HTML pages

| Protocol | HTML Serving | Example                                     |
|----------|--------------|---------------------------------------------|
| **WSGI** | ✅ Yes        | Django templates, Flask render_template     |
| **ASGI** | ✅ Yes        | FastAPI HTMLResponse, Django ASGI templates |

```
Content Type Support:
WSGI ── ✅ HTML, ✅ JSON, ✅ Static files
ASGI ── ✅ HTML, ✅ JSON, ✅ Static files, ✅ WebSockets, ✅ Server-Sent Events
```

## 4. Gunicorn + Uvicorn Workers Architecture

| Configuration          | Protocol Support | Architecture                      |
|------------------------|------------------|-----------------------------------|
| **Gunicorn (default)** | WSGI             | Built-in workers handle WSGI apps |
| **Gunicorn + Uvicorn** | ASGI             | Uvicorn workers handle ASGI apps  |

```
Gunicorn ASGI Setup:
[Gunicorn Master Process (Process Manager)] ──┬── [Uvicorn Worker 1 (ASGI)] ── [FastAPI App]
                                              ├── [Uvicorn Worker 2 (ASGI)] ── [FastAPI App]
                                              ├── [Uvicorn Worker 3 (ASGI)] ── [FastAPI App]
                                              └── [Uvicorn Worker 4 (ASGI)] ── [FastAPI App]
```

### Command Mapping

```bash
# Gunicorn WSGI (default)
gunicorn myapp.wsgi:application

# Gunicorn + Uvicorn (ASGI)
gunicorn main:app -k uvicorn.workers.UvicornWorker
```

## 5. Deployment Combinations

```
Development Patterns:
├── FastAPI Development ── uvicorn main:app
├── Django WSGI Development ── python manage.py runserver
├── Django ASGI Development ── uvicorn myproject.asgi:application
└── Flask Development ── flask run

Production Patterns:
├── FastAPI Production ── gunicorn main:app -k uvicorn.workers.UvicornWorker
├── Django WSGI Production ── gunicorn myproject.wsgi:application
├── Django ASGI Production ── gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker
└── Flask Production ── gunicorn myproject:app
```

## 6. Server-Framework Compatibility

| Web Server             | Compatible Frameworks | Command Example                                      |
|------------------------|-----------------------|------------------------------------------------------|
| **Uvicorn**            | FastAPI, Django ASGI  | `uvicorn main:app`                                   |
| **Gunicorn**           | Flask, Django WSGI    | `gunicorn app:application`                           |
| **Gunicorn + Uvicorn** | FastAPI, Django ASGI  | `gunicorn main:app -k uvicorn.workers.UvicornWorker` |

## 7. Decision Matrix - Performance is Important!

| Framework       | Protocol | Requests/sec* | Memory Usage | Recommendation                   |
|-----------------|----------|---------------|--------------|----------------------------------|
| **FastAPI**     | ASGI     | ~20,000       | Low          | ✅ **Primary choice**             |
| **Django ASGI** | ASGI     | ~15,000       | Medium       | ✅ **If Django ecosystem needed** |
| **Flask**       | WSGI     | ~5,000        | High         | ❌ **Avoid for new projects**     |
| **Django WSGI** | WSGI     | ~3,000        | High         | ❌ **Legacy mode only**           |

*Approximate benchmarks for typical API workloads

