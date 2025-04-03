from mcp.server.fastmcp import FastMCP, Context
from graphrag_mcp.documentation_tool import DocumentationGPTTool

# Create an MCP server
mcp = FastMCP("GraphRAG Documentation", 
               dependencies=["neo4j", "qdrant-client", "sentence-transformers"])

# Initialize the documentation tool
doc_tool = DocumentationGPTTool()

@mcp.tool()
def search_documentation(query: str, limit: int = 5, category: str = None) -> dict:
    """
    Search for documentation using semantic search and graph context expansion.
    
    Args:
        query: The search query to find relevant documentation
        limit: Maximum number of results to return (default: 5)
        category: Optional category to filter results (e.g., 'setup', 'api', 'usage')
        
    Returns:
        Dictionary with search results including chunks and related documents
    """
    return doc_tool.search_documentation(query, limit, category)

@mcp.tool()
def hybrid_search(query: str, limit: int = 5, category: str = None, expand_context: bool = True) -> dict:
    """
    Perform hybrid search using both vector similarity and graph context.
    
    Args:
        query: The search query to find relevant documentation
        limit: Maximum number of results to return (default: 5)
        category: Optional category to filter results (e.g., 'setup', 'api', 'usage')
        expand_context: Whether to expand results with graph context
        
    Returns:
        Dictionary with search results including chunks and related documents
    """
    return doc_tool.hybrid_search(query, limit, category, expand_context)

@mcp.resource("https://graphrag.db/schema/neo4j")
def get_graph_schema() -> str:
    """
    Get the Neo4j graph schema with node labels, relationship types, and property definitions.
    """
    try:
        schema = []
        with doc_tool.neo4j_driver.session() as session:
            # Get node labels
            result = session.run("""
            CALL db.labels() YIELD label
            RETURN collect(label) as labels
            """)
            labels = result.single()["labels"]
            schema.append("Node Labels: " + ", ".join(labels))
            
            # Get relationship types
            result = session.run("""
            CALL db.relationshipTypes() YIELD relationshipType
            RETURN collect(relationshipType) as types
            """)
            rel_types = result.single()["types"]
            schema.append("Relationship Types: " + ", ".join(rel_types))
            
            # Get property keys
            result = session.run("""
            CALL db.propertyKeys() YIELD propertyKey
            RETURN collect(propertyKey) as keys
            """)
            prop_keys = result.single()["keys"]
            schema.append("Property Keys: " + ", ".join(prop_keys))
            
            # Get node count by label
            schema.append("\nNode Counts:")
            for label in labels:
                count_query = f"MATCH (n:{label}) RETURN count(n) as count"
                count = session.run(count_query).single()["count"]
                schema.append(f"  {label}: {count}")
                
        return "\n".join(schema)
    except Exception as e:
        return f"Error retrieving graph schema: {str(e)}"

@mcp.resource("https://graphrag.db/collection/qdrant")
def get_vector_collection_info() -> str:
    """
    Get information about the Qdrant vector collection.
    """
    try:
        info = []
        collection_info = doc_tool.qdrant_client.get_collection(doc_tool.qdrant_collection)
        
        # Try to extract vectors count based on client version
        vectors_count = 0
        if hasattr(collection_info, 'vectors_count'):
            vectors_count = collection_info.vectors_count
        elif hasattr(collection_info, 'points_count'):
            vectors_count = collection_info.points_count
        
        info.append(f"Collection: {doc_tool.qdrant_collection}")
        info.append(f"Vectors Count: {vectors_count}")
        
        # Add vector configuration
        try:
            if hasattr(collection_info, 'config'):
                if hasattr(collection_info.config, 'params'):
                    vector_size = getattr(collection_info.config.params, 'vector_size', 'unknown')
                    info.append(f"Vector Size: {vector_size}")
                    
                    distance = getattr(collection_info.config.params, 'distance', 'unknown')
                    info.append(f"Distance Function: {distance}")
        except:
            info.append("Could not retrieve detailed vector configuration")
            
        return "\n".join(info)
    except Exception as e:
        return f"Error retrieving vector collection info: {str(e)}"

if __name__ == "__main__":
    mcp.run() 