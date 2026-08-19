import json
from ..db import get_connection, put_connection


class WidgetRepository:

    def create_widget(self, owner_id: str, widget) -> dict:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO widgets (owner_id, widget_type, title, description, config, button_text) "
                    "VALUES (%s, %s, %s, %s, %s, %s) "
                    "RETURNING id, owner_id, widget_type, title, description, config, button_text, created_at, updated_at"
                    (owner_id, widget.widget_type, widget.title, widget.description,
                     json.dumps(widget.config), widget.button_text),
                )
                row = cur.fetchone()
            conn.commit()
            # your turn: build and return the result from `row`
        finally:
            put_connection(conn)