# verdict

verdict is an agentic QA system that decides whether a test failure is real. Point it at any running backend (auth, role-gated routes, or file upload endpoints, regardless of language or framework, since it talks plain HTTP) with a plain-English scenario like "check that a viewer token can't hit the admin route," and a LangGraph agent classifies the scenario, generates structured test cases for it, runs them against the live app, and returns a verdict instead of a raw pass/fail. It's built to catch the thing traditional test scripts can't, the difference between a test that's actually broken and one that just got a flaky response, with full tracing on every step so you can see exactly why the agent decided what it decided.


Made with <3 by [woustachemax](https://www.siddharththakkar.xyz/)