"""SQL queries for visualization analytics - pure SQL logic"""


def get_outlier_detection_query(project_id: str) -> str:
    """Get SQL query to detect patents with anomalous number of components"""
    return f"""
    WITH component_stats AS (
      SELECT
        uri,
        ARRAY_LENGTH(components) AS num_components,
        AVG(ARRAY_LENGTH(components)) OVER() AS avg_components,
        STDDEV(ARRAY_LENGTH(components)) OVER() AS stddev_components
      FROM
        `{project_id}.patent_analysis.patent_knowledge_graph`
    )
    SELECT
      uri,
      num_components
    FROM
      component_stats
    WHERE
      -- A standard statistical definition of an outlier
      num_components > avg_components + (3 * stddev_components);
    """


def get_component_distribution_query(project_id: str) -> str:
    """Get SQL query to fetch component count distribution for histogram"""
    return f"""
    SELECT
      ARRAY_LENGTH(components) AS num_components
    FROM
      `{project_id}.patent_analysis.patent_knowledge_graph`
    WHERE
      ARRAY_LENGTH(components) > 0;
    """


def get_portfolio_analysis_query(project_id: str) -> str:
    """Get SQL query for strategic patent portfolio analysis bubble chart"""
    return f"""
    WITH
      patent_connection_stats AS (
        SELECT
          T1.uri,
          T1.applican,
          T2.invention_domain,
          (
            SELECT SUM(ARRAY_LENGTH(c.connected_to))
            FROM UNNEST(T2.components) AS c
            WHERE c.connected_to IS NOT NULL
          ) AS total_connections
        FROM
          `{project_id}.patent_analysis.ai_text_extraction` AS T1
        JOIN
          `{project_id}.patent_analysis.patent_knowledge_graph` AS T2
        ON
          T1.uri = T2.uri
        WHERE
          T1.applican IS NOT NULL AND T2.invention_domain IS NOT NULL
      )

    SELECT
      applican,
      COUNT(DISTINCT invention_domain) AS innovation_breadth,
      ROUND(AVG(total_connections), 2) AS average_connection_density,
      COUNT(uri) AS total_patents
    FROM
      patent_connection_stats
    WHERE
      total_connections > 0 -- Exclude patents with no connections to avoid skewing the average.
    GROUP BY
      applican
    HAVING
      COUNT(uri) > 1 -- Filter for applicants with more than one patent for a cleaner chart.
    ORDER BY
      total_patents DESC;
    """
