"""Definition of the GraphQL schema."""

import strawberry
from fastapi import APIRouter
from strawberry.extensions import AddValidationRules, QueryDepthLimiter
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from src.graphql_app.miscellanious import ValidateQueryParams, get_context
from src.graphql_app.mutations import Mutation
from src.graphql_app.queries import Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=True),
    extensions=[QueryDepthLimiter(3), AddValidationRules([ValidateQueryParams])],
)


graphql_router = APIRouter(tags=["GraphQL"])
graphql_router.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")
