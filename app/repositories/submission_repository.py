def create_submission(self, widget_id: str, data:dict, ip_address: str=None, 
                      country: str=None, city: str=None) -> dict:
    """
    Insert a new submission for a widget.

    ip_address/country/city are optional — geo enrichment happens BEFORE
    this method is called (in the service/route layer), and may have failed
    entirely (all providers down). The submission must still be saved either
    way, so these params default to None rather than being required.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO submissions (widget_id, data, ip_address, country, city)"
                "VALUES (%s, %s, %s, %s, %s) "
                "RETURNING id, widget_id, data, ip_address, country, city, created_at",
                (widget_id, json.dumps(data), ip_address, country, city),
            )
            row = cur.fetchone()
        conn.commit()
        return {
            "id": row[0],
            "widget_id": row[1],
            "data": row[2],
            "ip_address": row[3],
            "country": row[4],
            "city": row[5],
            "created_at": row[6],
        }
    finally:
        put_connection(conn)

def list_submissions(self, widget_id: str, owner_id: str) -> list[dict]:
    """
    Fetch all submissions for one widget, but only if that widget
    actually belongs to owner_id — enforced via JOIN against widgets,
    same tenant-isolation principle as everywhere else: a mismatch
    returns zero rows, not an error.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT s.id, s.widget_id, s.data, s.ip_address, s.country, s.city, s.created_at"
                " FROM submissions s"
                " JOIN widgets w ON s.widget_id = w.id"
                " WHERE w.id = %s AND w.owner_id = %s",
                (widget_id, owner_id),
            )
            rows = cur.fetchall()
        # return [ {...} for row in rows ]
        return [
            {
                "id": row[0],
                "widget_id": row[1],
                "data": row[2],
                "ip_address": row[3],
                "country": row[4],
                "city": row[5],
                "created_at": row[6],
            }
            for row in rows
        ]   
        
    finally:
        put_connection(conn)