# ready-4-prod-fastapi-app

A ready to go for production FastAPI app template.

# Table of Contents

1. [Inception](#inception)
   1. [Features](#features)
2. [Requirements](#requirements)
3. [Starting the API](#starting-the-api)
4. [Running QA Analysis](#running-qa-analysis)
5. [Interacting with GraphQL](#interacting-with-graphql)
   1. [Create a Transaction record](#create-a-transaction-record)
   2. [Create a Category record](#create-a-category-record)
   3. [Delete a Transaction record](#delete-a-transaction-record)
   4. [Delete a Category](#delete-a-category)
   5. [Fetch all transactions whose value are greater than 500](#fetch-all-transactions-whose-value-are-greater-than-500)
   6. [Fetch all transactions whose category name is `gift-list`](#fetch-all-transactions-whose-category-name-is-gift-list)
   7. [Update the category of a transaction](#update-the-category-of-a-transaction)
   8. [Update the description of a transaction](#update-the-description-of-a-transaction)

## Inception

This code contains a simple FastAPI application for tracking personal finance. It is built using FastAPI as the API
engine, SQLAlchemy for interacting with PostgreSQL and GraphQL for providing an interface for CRUD operations.

### Features

There are two main entities: `Category` and `Transactions`. Each transaction must belong to a category, e.g. `grocery`, `home-fixes`, etc.

CRUD operations can be done against both categories by the GraphQL interface. For more details on how to interact with the GraphQL endpoint, check the [Interacting with GraphQL](#interacting-with-graphql) section.

## Requirements

- Docker
- Python >= 3.12
- Poetry >= 1.8.5
- curl

## Starting the API

```bash
docker compose up api
```

## Running QA Analysis

```bash
poetry run pytest
```

```bash
poetry run mypy src --pretty
```

```bash
poetry run ruff check src
```

## Interacting with GraphQL

### Create a Transaction record

- Mutation:

```graphql
mutation createTransaction(
  $name: String!
  $value: Float!
  $category: String!
  $description: String
) {
  createTransaction(
    name: $name
    value: $value
    categoryName: $category
    description: $description
  ) {
    id
    createdAt
    updatedAt
    name
    description
    value
    categoryId
  }
}
```

- Variables:

```JSON
{
    "name": "Coffee with Mike",
    "value": 17.5,
    "category": "food",
    "description": "Coffe with Mike at Starbucks on Feb 22th"
}
```

### Create a Category record

- Mutation:

```graphql
mutation createCategory($name: String!) {
  createCategory(name: $name) {
    id
    createdAt
    updatedAt
    name
    transactions {
      name
    }
  }
}
```

- Variables:

```JSON
{
    "name": "food"
}
```

### Delete a Transaction record

- Mutation:

```graphql
mutation createTransaction(
  $name: String!
  $value: Float!
  $category: String!
  $description: String
) {
  createTransaction(
    name: $name
    value: $value
    categoryName: $category
    description: $description
  ) {
    id
    createdAt
    updatedAt
    name
    description
    value
    categoryId
  }
}
```

### Delete a Category

- Mutation:

```graphql
mutation deleteCategory($id: Int!) {
  deleteCategory(categoryId: $id) {
    success
    message
  }
}
```

- Variables:

```JSON
{
    "id": 9
}
```

### Fetch all transactions whose value are greater than 500

- Query:

```graphql
query listTransactions {
  transactions(filters: {value: {gt: 500}}) {
    items {
      id
      createdAt
      updatedAt
      name
      description
      value
      categoryId
      category {
        name
      }
    }
    totalItemsCount
  }
}
```

### Fetch all transactions whose category name is `gift-list`

- Query:

```graphql
query listCategories {
  categories(filters: {name: {eq: "gift-list"}}) {
    items {
      transactions {
        name
      }
    }
    totalItemsCount
  }
}
```

### Update the category of a transaction

- Mutation:

```graphql
mutation updateTransactionCategory {
  updateTransactionCategory(transactionId: 15, categoryId: 14) {
    name
    updatedAt
    category {
      name
    }
  }
}
```

### Update the description of a transaction

- Mutation:

```graphql
mutation updateDescription($transactionId: Int!, $description: String!) {
  updateTransactionDescription(
    transactionId: $transactionId
    description: $description
  ) {
    id
    name
    description
  }
}
```

- Variables:

```JSON
{
    "transactionId": 15,
    "description": "Dummy"
}
```

### Delete a transaction

- Mutation:

```graphql
mutation deleteTransaction($transactionId: Int!) {
  deleteTransaction(transactionId: $transactionId) {
    success
    message
  }
}
```

- Variables:

```JSON
{
    "transactionId": 15
}
```

### Delete a category (cascade effect)

- Mutation:

```graphql
mutation deleteCategory($categoryId: Int!) {
  deleteCategory(categoryId: $categoryId) {
    success
    message
  }
}
```

- Variables:

```JSON
{
    "categoryId": 2
}
```