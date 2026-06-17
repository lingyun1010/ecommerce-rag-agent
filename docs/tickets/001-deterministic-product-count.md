# Ticket 001: Deterministic Product Count Answers

## Status

Implemented

## Problem

Vector retrieval is useful for semantic customer-service questions, but it is not reliable for exact catalogue counting. In the previous example run, the question "how many products do you have" returned "three products listed" because the retriever only supplied a small product-table chunk to the LLM.

## Scope

Add a deterministic path for product-count questions:

- Parse `data/products.md` as a Markdown table.
- Count product rows directly.
- Answer count questions before falling back to the LlamaIndex query engine.
- Keep semantic product, policy, and FAQ questions on the existing RAG path.

## Acceptance Criteria

- Asking "how many products do you have" returns the full count from `data/products.md`.
- The answer states that the count comes from the local product catalogue rather than vector retrieval.
- Non-count questions continue to use the LlamaIndex retrieval flow.

## Implementation Notes

The helper functions live in `ecommerce_tools.py`, separate from the LlamaIndex setup, so structured ecommerce utilities can be tested without building the vector index or calling OpenAI.
