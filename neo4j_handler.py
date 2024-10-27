from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def create_user(self, user_data):
        query = """
        MERGE (u:User {id: $id})
        SET u.name = $name, u.screen_name = $screen_name, u.sex = $sex, u.city = $city
        """
        self.run_query(query, user_data)

    def create_group(self, group_data):
        query = """
        MERGE (g:Group {id: $id})
        SET g.name = $name, g.screen_name = $screen_name
        """
        self.run_query(query, group_data)

    def create_follow_relationship(self, user_from, user_to):
        query = """
        MATCH (u1:User {id: $from})
        MATCH (u2:User {id: $to})
        MERGE (u1)-[:FOLLOWS]->(u2)
        """
        self.run_query(query, {'from': user_from, 'to': user_to})

    def create_subscribe_relationship(self, user, group):
        query = """
        MATCH (u:User {id: $user})
        MATCH  (g:Group {id: $group})
        MERGE (u)-[:SUBSCRIBED]->(g)
        """
        self.run_query(query, {'user': user, 'group': group})

    def query_neo4j(self, query_type):
        queries = {
            'users_count': "MATCH (u:User) RETURN COUNT(u) AS count",
            'groups_count': "MATCH (g:Group) RETURN COUNT(g) AS count",
            'top_users_by_followers': """
                MATCH (u:User)<-[:FOLLOWS]-()
                RETURN u.id, u.name, COUNT(*) AS followers_count
                ORDER BY followers_count DESC LIMIT 5
            """,
            'top_groups_by_subscribers': """
                MATCH (g:Group)<-[:SUBSCRIBED]-()
                RETURN g.id, g.name, COUNT(*) AS subscribers_count
                ORDER BY subscribers_count DESC LIMIT 5
            """,
            # По сути данное условие никогда не выполнится, т.к в таком случае юзеры - друзья 
            'mutual_followers': """
                MATCH (u1:User)-[:FOLLOWS]->(u2:User)-[:FOLLOWS]->(u1) 
                RETURN u1.id, u2.id
            """
        }

        try:
            result = self.run_query(queries[query_type])
            return result
        except KeyError as ke:
            logger.error(f"Запроса {query_type} не существует")  
            return []      