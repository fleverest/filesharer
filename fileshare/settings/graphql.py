from pydantic import BaseModel

class GraphQLSettings(BaseModel):

    """A class for keeping settings for the graphql interface"""

    default_page_size: int
    pagination_limit: int
