# Architecture

## Overview

ResumeMatch AI is a two-tier web app: a static frontend and a small Flask API. There is no database — every analysis is a stateless, single request/response cycle.