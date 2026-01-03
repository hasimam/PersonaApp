# Technical Design Document -- Personality Matching App

## System Overview

A personality-based recommendation system using trait vectors and
similarity matching.

------------------------------------------------------------------------

## Data Model

### Traits

-   8--12 normalized traits (0--100)

### Tables

-   Users
-   Questions
-   Traits
-   Idol Profiles
-   Results

------------------------------------------------------------------------

## Test Scoring Engine

-   Likert scale inputs
-   Trait aggregation
-   Reverse scoring
-   Normalization

------------------------------------------------------------------------

## Matching Algorithm

### Vector Representation

User and idol profiles stored as numeric vectors.

### Similarity Metric

Cosine similarity (primary).

### Output

Ranked list → Top 3 idols.

------------------------------------------------------------------------

## Tech Stack

### Frontend

-   React / React Native / Flutter

### Backend

-   Node.js or FastAPI

### Database

-   PostgreSQL or Firebase

------------------------------------------------------------------------

## Analytics

-   Completion rate
-   Drop-off points
-   Match popularity
-   Retention

------------------------------------------------------------------------

## Validation

-   Consistency tests
-   Random-response detection
