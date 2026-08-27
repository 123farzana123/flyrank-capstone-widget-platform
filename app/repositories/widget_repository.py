import json
from ..db import get_connection, put_connection
from typing import Optional

class WidgetRepository:

    def create_widget(self, owner_id: str, widget) -> dict:

        """
        Insert a new widget row owned by `owner_id`.

        `owner_id` comes from the authenticated user's JWT (Supabase `sub` claim),
        never from the request body — this is what enforces tenant isolation at
        creation time, so a widget always belongs to whoever is actually logged in.

        `widget.config` is a Python dict (from the WidgetCreate schema) and must be
        serialized to a JSON string via json.dumps() before being passed to psycopg2,
        since Postgres's JSONB column expects text on the way in. On the way OUT
        (see RETURNING + fetchone), psycopg2 automatically deserializes JSONB back
        into a Python dict, so no json.loads() is needed when reading `row[5]`.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO widgets (owner_id, widget_type, title, description, config, button_text) "
                    "VALUES (%s, %s, %s, %s, %s, %s) "
                    "RETURNING id, owner_id, widget_type, title, description, config, button_text, created_at, updated_at",
                    (owner_id, widget.widget_type, widget.title, widget.description,
                     json.dumps(widget.config), widget.button_text),
                )
                row = cur.fetchone()
            conn.commit()
            return {
                "id": row[0],
                "owner_id": row[1],
                "widget_type": row[2],
                "title": row[3],
                "description": row[4],
                "config": row[5],
                "button_text": row[6],
                "created_at": row[7],
                "updated_at": row[8],
            }
        finally:
            put_connection(conn)


    def get_widget(self, widget_id: str, owner_id: str) -> Optional[dict]:
        """
        Fetch one widget by id, scoped to owner_id.

        The WHERE clause checks BOTH id and owner_id together — if the widget
        belongs to a different owner, this returns no row, identical to the
        widget not existing at all. This is what makes the API return 404
        (not 403) for other tenants' widgets: we never reveal that a widget
        with this id exists if the caller doesn't own it.
        """
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, owner_id, widget_type, title, description, config, button_text, created_at, updated_at "
                    "FROM widgets WHERE id = %s AND owner_id = %s",
                    (widget_id, owner_id),
                )
                row = cur.fetchone()
            return {
                "id": row[0],
                "owner_id": row[1],
                "widget_type": row[2],
                "title": row[3],
                "description": row[4],
                "config": row[5],
                "button_text": row[6],
                "created_at": row[7],
                "updated_at": row[8],
            } if row else None
        finally:
            put_connection(conn)


    def list_widgets(self, owner_id: str) -> list[dict]:

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, owner_id, widget_type, title, description, config, button_text, created_at, updated_at "
                    "FROM widgets WHERE owner_id = %s",
                    (owner_id,),
                )
                rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "owner_id": row[1],
                    "widget_type": row[2],
                    "title": row[3],
                    "description": row[4],
                    "config": row[5],
                    "button_text": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                }
                for row in rows
            ]
        finally:
            put_connection(conn)


    def update_widget(self, widget_id: str, owner_id: str, widget) -> Optional[dict]:
        """
        Update an existing widget's editable fields, scoped to owner_id.

        widget_type is deliberately NOT updatable — changing it would leave
        `config` in a shape that no longer matches the widget's type (e.g. a
        signup_form's config wouldn't make sense on a cta_popover). To change
        type, delete this widget and create a new one instead.

        Same tenant-isolation pattern as get_widget: WHERE id AND owner_id
        together means a mismatch returns no row -> None -> 404, never 403.
        """

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE widgets SET title=%s, description=%s, config=%s, button_text=%s, updated_at=now() "
                    "WHERE id=%s AND owner_id=%s "
                    "RETURNING id, owner_id, widget_type, title, description, config, button_text, created_at, updated_at",
                    (widget.title, widget.description, json.dumps(widget.config),
                    widget.button_text, widget_id, owner_id),
                )
                row = cur.fetchone()
            conn.commit()
            return {
                    "id": row[0],
                    "owner_id": row[1],
                    "widget_type": row[2],
                    "title": row[3],
                    "description": row[4],
                    "config": row[5],
                    "button_text": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                } if row else None
            
        finally:
            put_connection(conn)


    def delete_widget(self, widget_id: str, owner_id: str) -> bool: 
        """
        Delete an existing widget, scoped to owner_id.

        Same tenant-isolation pattern as get_widget: WHERE id AND owner_id
        together means a mismatch returns no row -> None -> 404, never 403.
        """

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM widgets WHERE id=%s AND owner_id=%s ",
                    (widget_id, owner_id),
                )
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
            
        finally:
            put_connection(conn)