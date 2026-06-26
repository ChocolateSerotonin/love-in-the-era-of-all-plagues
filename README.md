Computational Narrative Simulation Inspired by Gabriel García Márquez

Project Overview

This project explores a simple question:

Can a literary theme be transformed into a computational model?

Rather than retelling Love in the Time of Cholera, this project extracts one of its central ideas—the lifelong journey from worldly attachment toward essential love—and represents it as a parameterized simulation.

Users adjust a small number of psychological and environmental variables, while the simulator generates a unique life trajectory and automatically identifies important narrative events such as turning points, breakthroughs and moments of realization.

The project is an exploration of the intersection between literature, narrative modeling, human psychology and AI-assisted creativity.

Motivation

Large Language Models are becoming increasingly capable of generating fluent stories.

However, many literary qualities remain difficult to model explicitly:

long-term character development
narrative rhythm
emotional accumulation
symbolic turning points
gradual transformation of values

This project investigates whether these abstract literary concepts can first be represented as explicit computational structures before being incorporated into AI-assisted storytelling systems.

Core Design
1. Parameterized Character Model

Each simulation starts from several user-controlled variables, including:

Persistence
Life Volatility
Discipline
Randomness
Initial Belief

Rather than determining a fixed ending, these parameters influence how the protagonist gradually evolves throughout life.

2. Narrative Path Generator

The simulator generates continuous life trajectories using two complementary mechanisms:

Continuous evolution (smooth development)
Event-driven evolution (discrete life events)

Different parameter combinations produce dramatically different narrative curves.

3. Emergent Narrative Events

Instead of manually writing stories, the simulator detects meaningful moments algorithmically.

Examples include:

Growth acceleration
Turning points
Collapse
Recovery
Enlightenment

These events are identified through first-order derivatives, second-order derivatives, local extrema and other numerical properties of the generated trajectory.

4. Interactive Storytelling

Users can continuously modify parameters through a Streamlit interface and immediately observe changes in:

life trajectory
narrative timeline
emotional evolution

The simulator therefore serves as an experimental platform rather than a fixed story.

Technical Stack
Python
Streamlit
NumPy
Matplotlib
DeepSeek (concept development and iterative prompt design)
Why This Project

This project is not intended to reproduce Love in the Time of Cholera.

Instead, it explores a broader research question:

Can literary aesthetics be abstracted into computational representations?

It is also an experiment in combining:

Computational Narrative
Human-centered AI
Interactive Storytelling
Literary Analysis
